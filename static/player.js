export class Player {
    constructor(){
    this.player = document.getElementById('player');
    this.player.addEventListener("ended",this.handleEvents);

    this.src = ""
    this.trackNo = 0;
    }
    async play(){
        try{
        await this.player.play();
        document.querySelector('#nowPlaying').innerHTML = `${window.myPlayerData[this.trackNo]}`;
        }
        catch (err){
        }
    }

    set src(value) {
        this._src = value;
        this.player.src = this._src;
        return;
    }
    get src() {
        return this._src;
    }
    handleEvents = (event) => {
        switch(event.type){
            case "ended":
                this.playNextTrack();
                break;
            default:
                console.log("Unregistered event.type detected.")
        }
    }

    playNextTrack(){
        if (this.trackNo+1 < window.myPlayerData.length){
            this.trackNo += 1;
            this.updateSrc();
            this.play();

        }

    }
    updateSrc(trackNo=this.trackNo){
        this.trackNo = trackNo;
        let directoryPath = window.myPlayerData[trackNo][0];
        let fileName = window.myPlayerData[trackNo][1];
        let uri = `stream?dir=${directoryPath}&fname=${fileName}`;

        if(this.src != uri){
            this.src = uri;
        }
        this.play();
    }
}