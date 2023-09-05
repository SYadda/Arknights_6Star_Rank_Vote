import pickle

with open('list/win_score.pickle', 'rb') as f:
    lst_win_score = pickle.load(f)
with open('list/lose_score.pickle', 'rb') as f:
    lst_lose_score = pickle.load(f)

lst_win_score.append(100)
lst_lose_score.append(100)

with open('list/win_score.pickle', 'wb') as f:
    pickle.dump(lst_win_score, f)
with open('list/lose_score.pickle', 'wb') as f:
    pickle.dump(lst_lose_score, f)