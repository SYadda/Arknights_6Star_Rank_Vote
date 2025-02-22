const STORAGE_RESULT = 'local_vote_result'

export const useLocalVoteStore = defineStore('localVote', () => {
  const result = useStorage(STORAGE_RESULT, {})

  function createOpterData(data = {}) {
    return { win_times: 0, lose_times: 0, scores: 0, vote_times: 0, win_rate: -1, ...data }
  }

  function getOpterData(name) {
    return result.value[name] || createOpterData()
  }

  function updateResult(name, data) {
    const opter = result.value[name] || createOpterData()
    result.value = { ...result.value, [name]: { ...opter, ...data } }
  }

  function assignWinner(name) {
    const opter = getOpterData(name)
    updateResult(name, {
      vote_times: opter.vote_times + 1,
      win_times: opter.win_times + 1,
      scores: opter.scores + 1,
      win_rate: ((opter.win_times + 1 / (opter.vote_times + 1)) * 100).toFixed(2),
    })
  }

  function assignLoser(name) {
    const opter = getOpterData(name)
    updateResult(name, {
      vote_times: opter.vote_times + 1,
      lose_times: opter.lose_times + 1,
      scores: opter.scores - 1,
      win_rate: ((opter.win_times / (opter.vote_times + 1)) * 100).toFixed(2),
    })
  }

  function getFinalOrder() {
    const name = []
    const rate = []
    const score = []

    const entries = Object.entries(result.value)
      .map(([name, { win_rate, scores }]) => ({ name, rate: win_rate, score: scores }))
      .sort((a, b) => b.rate - a.rate)

    entries.forEach((d) => {
      name.push(d.name)
      rate.push(d.rate)
      score.push(d.score)
    })

    return { name, rate, score }
  }

  return {
    result,
    assignWinner,
    assignLoser,
    getFinalOrder,
  }
})
