export class Player {
    constructor(){
    this.player = document.getElementById('player');
    this.player.addEventListener("ended",this.handleEvents);
    this.player.addEventListener("volumechange",this.handleEvents);
    document.querySelector("#row_pointer").addEventListener("click", ()=>{this.scrollToRow()});
    addEventListener("scroll",() => {this.updateDivPosition()});
    this.divOpacity = 0;

    this.src = ""
    this.trackNo = 0;
    this.srcSet = false;
    this.playingRow;
    }

    async play(){
        try{
        await this.player.play();
        let dataArray = this.playingRow.firstChild.children[1].value.split('||');
        let album = dataArray[0];
        let artist = dataArray[5];
        let date = dataArray[3];
        date = date.slice(0,4);
        let title = dataArray[4];
        let displayString = `${album} || ${artist} || ${title} || (${date})`;
        displayString = displayString.replaceAll("_"," ");
        document.querySelector('#nowPlaying').innerHTML = displayString;
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
            case "play":
                if(!this.interval){
                this.handleInterval();
                }
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
    updateSrc(element, trackNo=this.trackNo){
        this.trackNo = trackNo;
        let directoryPath = window.myPlayerData[trackNo][0];
        let fileName = window.myPlayerData[trackNo][1];
        let uri = `stream?dir=${directoryPath}&fname=${fileName}`;

        if(this.src != uri){
            this.src = uri;
        }
        this.play();
        if(element){
            this.playingRow = element.parentElement.parentElement;
        }
        else{
            this.playingRow = this.playingRow.nextElementSibling;
        }
        this.indicatePlaying();
    }
    indicatePlaying(){
//         this.playingRow.style.backgroundColor = "#34eb6e";
         let floater = document.querySelector("#floating-div");
         const rect = this.playingRow.getBoundingClientRect();
//         floater.style.position = "absolute";
         floater.style.left = rect.left + window.scrollX + 'px';
         floater.style.top = rect.top + window.scrollY + 'px';
         floater.style.height = rect.height + 'px';
         floater.style.width = rect.width + 'px';
//         floater.style.backgroundColor = "#34eb6e";
         floater.style.opacity = "0.5";
    }
    updateDivPosition(){
        if(this.srcSet === true){
        this.indicatePlaying();
        }
    }
    scrollToRow(){
        this.playingRow.scrollIntoView({block: "end", inline: "nearest"});
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
