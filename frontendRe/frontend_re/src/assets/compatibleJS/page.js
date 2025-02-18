export class Hero {
    constructor(name, data = {win_times: 0, lose_times: 0, scores:  0, vote_times:  0, win_rate: -1}) {
        this.name = name;
        this.win_times = data.win_times;
        this.lose_times = data.lose_times;
        this.scores = data.scores;
        this.vote_times = data.vote_times;
        this.win_rate = data.win_rate;
    }

    win() {
        this.vote_times++;
        this.win_times++;
        this.scores++;
        this.win_rate = ((this.win_times / this.vote_times) * 100).toFixed(2);
    }

    lose() {
        this.vote_times++;
        this.lose_times++;
        this.scores--;
        this.win_rate = ((this.win_times / this.vote_times) * 100).toFixed(2);
    }

    set_attr(dict) {
        this.name = dict["name"];
        this.win_times = dict["win_times"];
        this.lose_times = dict["lose_times"];
        this.scores = dict["scores"];
        this.vote_times = dict["vote_times"];
        this.win_rate = dict["win_rate"];
    }
}