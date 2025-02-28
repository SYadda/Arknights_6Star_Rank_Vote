package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"sort"
	"sync"
	"sync/atomic"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	pb "ark-vote/proto"
	"slices"
)

var (
	serverAddr  = flag.String("addr", "localhost:10000", "服务器地址")
	concurrency = flag.Int("c", 500, "并发数量")
	total       = flag.Int("n", 100000, "总请求数量")
)

var timeBuckets = []float64{
	1, 2, 5, 10, 20, 50,
	100, 200, 500,
	1000, 2000, 5000,
	10000,
}

type Histogram struct {
	buckets []uint64
	mu      sync.Mutex
}

type Result struct {
	success   uint64
	failure   uint64
	total     uint64
	histogram *Histogram
}

type workerResult struct {
	success   uint64
	failure   uint64
	durations []time.Duration
}

func NewHistogram() *Histogram {
	return &Histogram{
		buckets: make([]uint64, len(timeBuckets)+1),
	}
}

func (h *Histogram) Add(d time.Duration) {
	ms := d.Seconds() * 1000
	h.mu.Lock()
	defer h.mu.Unlock()

	idx := sort.SearchFloat64s(timeBuckets, ms)
	if idx < len(timeBuckets) && ms == timeBuckets[idx] {
		idx++
	}
	h.buckets[idx]++
}

func (h *Histogram) Statistics() (map[float64]time.Duration, time.Duration) {
	h.mu.Lock()
	defer h.mu.Unlock()

	var total uint64
	for _, count := range h.buckets {
		total += count
	}
	if total == 0 {
		return nil, 0
	}

	percentiles := []float64{50, 90, 95, 99}
	results := make(map[float64]time.Duration)
	remainingPercentiles := make([]float64, len(percentiles))
	copy(remainingPercentiles, percentiles)

	var current uint64
	for i, upperBound := range timeBuckets {
		bucketMin := 0.0
		if i > 0 {
			bucketMin = timeBuckets[i-1]
		}

		bucketCount := h.buckets[i]
		if bucketCount == 0 {
			continue
		}

		for pIdx := 0; pIdx < len(remainingPercentiles); {
			p := remainingPercentiles[pIdx]
			target := float64(total) * p / 100

			if float64(current) < target && target <= float64(current+bucketCount) {
				position := (target - float64(current)) / float64(bucketCount)
				estimated := bucketMin + position*(upperBound-bucketMin)
				results[p] = time.Duration(estimated * float64(time.Millisecond))

				remainingPercentiles = slices.Delete(remainingPercentiles, pIdx, pIdx+1)
			} else {
				pIdx++
			}
		}

		current += bucketCount
	}

	overflowCount := h.buckets[len(h.buckets)-1]
	if overflowCount > 0 {
		maxDuration := time.Duration(timeBuckets[len(timeBuckets)-1]) * time.Millisecond
		for _, p := range remainingPercentiles {
			results[p] = maxDuration
		}
	}

	return results, time.Duration(timeBuckets[len(timeBuckets)-1]) * time.Millisecond
}

func main() {
	flag.Parse()

	globalResult := &Result{
		histogram: NewHistogram(),
	}

	var wg sync.WaitGroup
	results := make(chan workerResult, *concurrency)

	connPool := make(chan *grpc.ClientConn, *concurrency)
	for range *concurrency {
		conn, err := grpc.NewClient(
			*serverAddr,
			grpc.WithTransportCredentials(insecure.NewCredentials()),
		)
		if err != nil {
			log.Fatalf("无法连接: %v", err)
		}
		connPool <- conn
	}

	start := time.Now()
	requestsPerRoutine := *total / *concurrency

	for range *concurrency {
		wg.Add(1)
		go func() {
			defer wg.Done()
			localRes := workerResult{
				durations: make([]time.Duration, 0, requestsPerRoutine),
			}

			for range requestsPerRoutine {
				conn := <-connPool
				startTime := time.Now()
				err := vote(conn)
				duration := time.Since(startTime)
				connPool <- conn

				if err != nil {
					localRes.failure++
				} else {
					localRes.success++
				}
				localRes.durations = append(localRes.durations, duration)
			}
			results <- localRes
		}()
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	for res := range results {
		atomic.AddUint64(&globalResult.success, res.success)
		atomic.AddUint64(&globalResult.failure, res.failure)
		atomic.AddUint64(&globalResult.total, res.success+res.failure)

		for _, d := range res.durations {
			globalResult.histogram.Add(d)
		}
	}

	close(connPool)
	for conn := range connPool {
		conn.Close()
	}

	percentileValues, maxDuration := globalResult.histogram.Statistics()
	totalCount := atomic.LoadUint64(&globalResult.total)
	durationTotal := time.Since(start)

	fmt.Println("\n压测结果:")
	fmt.Printf("总请求数: %d\n", totalCount)
	fmt.Printf("成功数: %d\n", atomic.LoadUint64(&globalResult.success))
	fmt.Printf("失败数: %d\n", atomic.LoadUint64(&globalResult.failure))
	fmt.Printf("总耗时: %v\n", durationTotal)
	fmt.Printf("QPS: %.2f\n", float64(totalCount)/durationTotal.Seconds())

	if totalCount > 0 {
		sum := 0.0
		globalResult.histogram.mu.Lock()
		for i, count := range globalResult.histogram.buckets {
			var bucketMax float64
			if i < len(timeBuckets) {
				bucketMax = timeBuckets[i]
			} else {
				bucketMax = timeBuckets[len(timeBuckets)-1]
			}
			bucketMin := 0.0
			if i > 0 {
				bucketMin = timeBuckets[i-1]
			}
			avg := (bucketMin + bucketMax) / 2
			sum += avg * float64(count)
		}
		globalResult.histogram.mu.Unlock()
		average := time.Duration(sum/float64(totalCount)) * time.Millisecond
		fmt.Printf("Average: %v\n", average)
	}

	if len(percentileValues) > 0 {
		fmt.Println("\n响应时间分布 (分桶统计):")
		for _, p := range []float64{50, 90, 95, 99} {
			if val, ok := percentileValues[p]; ok {
				fmt.Printf("P%.0f: %v\n", p, val)
			}
		}
		fmt.Printf("Max: %v\n", maxDuration)
	}
}

func vote(conn *grpc.ClientConn) error {
	client := pb.NewVotingServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	createResp, err := client.CreateBallot(ctx, &pb.CreateBallotRequest{
		Topic: "test1",
		Identity: &pb.Identity{
			Fingerprint: "fingerprint",
			Ip:          "127.0.0.1",
			IsMobile:    false,
		},
	})
	if err != nil {
		println("CreateBallot失败: ", err)
		return fmt.Errorf("CreateBallot失败: %w", err)
	}

	_, err = client.SubmitVote(ctx, &pb.SubmitVoteRequest{
		TopicId: createResp.GetTopicId(),
		Topic:   "test1",
		Identity: &pb.Identity{
			Fingerprint: "fingerprint",
			Ip:          "127.0.0.1",
			IsMobile:    false,
		},
		BallotCode:     createResp.GetBallotCode(),
		SelectedOption: []int32{createResp.GetOptions()[0]},
		ExcludedOption: []int32{createResp.GetOptions()[1]},
	})
	if err != nil {
		println("SubmitVote失败: ", err)
		return fmt.Errorf("SubmitVote失败: %w", err)
	}

	return nil
}
