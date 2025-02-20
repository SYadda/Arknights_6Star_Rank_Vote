import { apiNewCompare } from '@/api/new_compare'
import { apiSaveScore } from '@/api/save_score'

const STORAGE_TIMES = 'vote_times'

export const useCompareStore = defineStore('compare', () => {
  const { update: upOpter1, operator: opter1 } = useOperator()
  const { update: upOpter2, operator: opter2 } = useOperator()

  const voteTimes = useStorage(STORAGE_TIMES, 0)

  getNewCompare()

  function updateCompare(data) {
    upOpter1(data.left)
    upOpter2(data.right)
  }

  function getNewCompare() {
    apiNewCompare(updateCompare)
  }

  const { assignWinner, assignLoser } = useLocalVoteStore()
  function voteForWinner(opter) {
    const [winner, loser] = opter.name === opter1.name ? [opter1, opter2] : [opter2, opter1]
    assignWinner(winner.name)
    assignLoser(loser.name)

    voteTimes.value++

    apiSaveScore({
      win_id: winner.id,
      lose_id: loser.id,
    }, () => {
      getNewCompare()
    })
  }

  return {
    operator1: opter1,
    operator2: opter2,
    voteForWinner,
  }
})
