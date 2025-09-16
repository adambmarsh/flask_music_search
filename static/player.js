export class Player {
    constructor(){
    this.player = document.getElementById('player');
    this.player.addEventListener("ended",this.handleEvents);
    this.player.addEventListener("volumechange",this.handleEvents);

    this.src = ""
    this.trackNo = 0;
    this.srcSet = false;
    }
    async play(){
        try{
        await this.player.play();
        document.querySelector('#nowPlaying').innerHTML = `${decodeURIComponent(window.myPlayerData[this.trackNo])}`;
        }
        catch (err){
        }
    }

    set src(value) {
        this._src = value;
        this.player.src = this._src;
        if(this.srcSet === false){
            this.player.volume = this.getVolumeFromCookie();
            this.srcSet = true;
        }
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
            case "volumechange":
                this.updateVolumeCookie();
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
    updateVolumeCookie(){
        let d = new Date();
        const month = d.getMonth();
        if (month+3 < 13){
            d.setMonth(month+3);
        }
        else{
            let year = d.getYear();
            d.setYear(year+1);
            d.setMonth((month+3 % 12));
        }
        const formatted_date = d.toUTCString();
        const path = "path=/";
        let volume = this.player.volume;
        document.cookie = `volume=${volume};expires=${formatted_date};${path}`;
    }
    getVolumeFromCookie(){
        let volume = this.player.volume;
        if(document.cookie != ''){
            let cookieArray = document.cookie.split('=');
            volume = parseFloat(cookieArray[1]);
        }
        return volume;

    }
}