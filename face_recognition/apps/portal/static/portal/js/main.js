/** CSRF Protection **/
    var csrf = $("[name=csrfmiddlewaretoken]").val();
    
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        }
    });
    /** End CSRF Protection **/

    var imageSuccessCount = 0,
        imagePending = 0;
    var imageData = [];
    var avatar = $("#avatar");
    var status_text = $(".status_text");
    var canvas = document.getElementById("canvas");
    var video = document.getElementById("video");
    var alert = $("#mainAlert");
    var progress = $("#imageProgress");
    var vstream = null;
    var available_mood_classes = ["fa-smile-beam", "fa-frown-open", "fa-angry"];
    var terminal = $("#terminalttx");
    var user = null;
    var feeds = [];
    var feedCheckers = {
        'news': true,
        'videos': true,
        'interval': false,
        'timeout': false
    }

    function GetCameraPermissions() {
        if (!navigator.mediaDevices) {
            alert("MediaDevices API is not supported on your browser! Exiting!");
            return;
        }
        if (!navigator.mediaDevices.enumerateDevices)
            $("#cameraPopup").show();
        return navigator.mediaDevices.getUserMedia({
            video: true,
            // audio: true
        }).then(cameraInitialized);
    }

    function resetCaptureFrames() {
        imageSuccessCount = 0;
        imagePending = 0;
        imageData = [];
    }

    function cameraInitialized(stream) {
        $("#cameraPopup").fadeOut();
        video.srcObject = stream;
        vstream = stream;
        video.play();
        avatar.fadeOut();
        $("#video").fadeIn();
    }

    function startCapturingFrames(callback) {

        console.log("Starting");
        $("#faceDetector").fadeIn();
        var frame = captureFrame();
        callback(frame);
    }

    function captureFrame() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        var context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        var data = canvas.toDataURL();
        return data;
    }

    function stopCapturingFrames() {
        vstream.getTracks()[0].stop();
    }

    function startMoodDetection(frame) {
        logTerminal("Preparing Mood Detection Engine...");
        stopCapturingFrames();
        let payload = prepareImagePayload(frame);
        // logTerminal("Preparing Payload for server...Connecting to server...");
        $(".current_mood").html($(".current_mood").html() + ' <i class="fas fa-spin fa-circle-notch"></i>');
        $.ajax({
            url: api_endpoints['detect_mood'],
            data: payload,
            type: 'POST',
            success: function (response) {
                if (response.status) {
                    moodData = response.mood;
                    loadMoodData();
                } else {
                    $(".current_mood").html("Error!");
                }
            }
        });
    }

    function loadMusic(emotion) {}

    function getB64Data(data) {
        // return data;
        return data.split(",")[1];
    }

    function prepareImagePayload(data) {
        var b64Image = getB64Data(data);
        var postData = {
            "image": b64Image
        };
        console.log(postData)
        return postData;
    }

    function setClock() {
        let days = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"];
        let months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "December"];
        setInterval(function (e) {
            var curr = new Date();
            $("#date_num").html(curr.getDate());
            $("#time_num").html(curr.getHours() + ":" + curr.getMinutes());
            $("#day").html(days[curr.getDay() - 1]);
            $("#month").html(months[curr.getMonth()]);
            $("#second").html(curr.getSeconds());
        }, 1000);
    }

    function loadUser() {
        if (user != null)
            return
        $.ajax({
            url: api_endpoints['get-logged-in-user'],
            method: 'GET',
            dataType: 'JSON',
            success: function (response) {
                if (response.status) {
                    user = response.data;
                    loadUserData();
                } else {
                    window.location.reload();
                }
            }
        })
    }

    function loadUserData() {
        if (user == null)
            return

        logTerminal("Initialising user data, Hello " + user.name);

        $(".user_name").html(user.name);
    }

    function loadMoodData() {
        if (moodData == null)
            return
        $(".current_mood").html(moodData.mood);
        let score = '';
        let health_score = moodData.health_score;
        if(health_score > 80)
            score = 'Chilled'
        else{
            if(health_score > 60)
                score = "You'll be okay"
            else {
                if(health_score > 50)
                    score = "I'm worried"
                else {
                    if(health_score > 30)
                        score = "Goto Doctor"
                    else
                        score = "Help Required!!"
                }

            }
        }
        $(".current_mood_score").html(score + " (" + Math.round(moodData.health_score) + "%)");
        logTerminal("You seem to be " + moodData.mood + "...");
        logTerminal("Salman Khan just messaged.. 'My Emotion is my emotion'");
        logTerminal("'None of your emotion'");
        loadSpotifyPlayer();
        setTimeout(function () {
            GetCameraPermissions();
            $(video).one('canplay', function () {
                startCapturingFrames(startMoodDetection);
            });
        }, 60000);
    }

    function loadSpotifyPlayer(){
        $("#music_loader").fadeIn();
        $.ajax({
            url: api_endpoints['spotify'],
            dataType: 'JSON',
            method: 'GET',
            success: function(response){
                if(response.status){
                    if(response.data){
                        $("#music_feed").fadeOut().html("").fadeIn();
                        for(let track in response.data.tracks){
                            let id = response.data.tracks[track].id;
                            let html_data = generateSpotifyData(response.data.tracks[track], id);
                            let html = generateFeedComponent(html_data, {"data-spotify-url": response.data.tracks[track].uri}, 'spotify');
                            $("#music_feed").append(html);
                            // bindSpotify(id);
                        }
                        logTerminal("Curating Music for your mood...");
                    }
                }
                $("#music_loader").fadeOut();
            },
            error: function(e){
                $("#music_loader").fadeOut();
            }
        });
    }
    function bindSpotify(id){ 
        $("#feed-" + id + " a").on("click", function(e){
            e.preventDefault();
            let spotify_url = $(this).attr("data-spotify-url");
              play({
                playerInstance: new Spotify.Player({ name: "..." }),
                spotify_uri: spotify_url,
              });

        });
    }

    var terminal_queue = ["Initialising", ];
    var typed = null;
    var terminal_empty = true;

    function logTerminal(msg) {
        terminal_queue.push(msg);
    }

    function loadNextForTerminal() {
        console.log("Poll");
        console.log(terminal_queue);
        console.log(terminal_empty);
        if (!terminal_empty) return;
        if (terminal_queue.length == 0) return;
        // if(typed) typed.destroy();
        terminal_empty = false;
        terminal.fadeIn();
        typed = new Typed(terminal[0], {
            strings: ["", terminal_queue.shift()],
            typeSpeed: 5,
            loop: false,
            loopCount: 1,
            contentType: 'html',
            backDelay: 200,
            onStart: function (self) {
                // terminal.fadeIn();
                terminal_empty = false;
            },
            onComplete: function (self) {
                setTimeout(function () {
                    terminal.fadeOut();
                    setTimeout(function () {
                        typed.destroy();
                        terminal_empty = true;
                    }, 500);
                }, 500);
            },
            onDestroy: function (self) {
                // terminal_empty = true;
            }
        });
    }

    function saveFeed(feed, type, source=null){
        feeds.push({
            'feed': feed,
            'type': type,
            'source': source,
            'inserted': false
        })
    }
    function getFeed(){
        $("#feed-loader").fadeIn();
        feedCheckers.videos = false;
        $.ajax({
            url: api_endpoints['get-youtube-videos'],
            dataType: 'JSON',
            method: 'GET',
            success: function(response){
                if(response.status){
                    for(let x in response.data){
                        let v = response.data[x];
                        saveFeed(v, 'youtube', 'YouTube');
                    }
                    feedCheckers.videos = true;
                    populateFeed();
                }
            },
            error: function(response){
                feedCheckers.videos = true;
                logTerminal("Failed to load videos...");
            }
        });
        feedCheckers.news = false;
        $.ajax({
            url: api_endpoints['get-news'],
            dataType: 'JSON',
            method: 'GET',
            success: function(response){
                if(response.status){
                    for(let x in response.data){
                        let v = response.data[x];
                        let source = null;
                        if(v.source && v.source.name)
                            source = v.source.name
                        saveFeed(v, 'news', source);
                    }
                    populateFeed();
                    feedCheckers.news = true;
                }
            },
            error: function(response){
                feedCheckers.news = true;
                logTerminal("Failed to load news...");
            }
        });
        feedCheckers.timeout = false;
    }

    function loadFeed(){
        if(feedCheckers.interval != false)
            return
        setTimeout(getFeed, 1);
        feedCheckers.interval = setInterval(function(){
            console.log(feedCheckers);
            if(feedCheckers.videos == true && feedCheckers.news == true){
                $("#feed-loader").fadeOut();
                if(feedCheckers.timeout == false)
                    feedCheckers.timeout = setTimeout(getFeed, 60000);
            }
        }, 5000);
    }

    function populateFeed(){
        console.log(feeds);
        logTerminal("Preparing your feed...");
        for(let x in feeds){
            let feed = feeds[x];
            if(feed.inserted) continue;
            let html = null;
            let id = new Date().getTime();
            if(feed.type == 'youtube'){
                html = generateFeedComponent(generateYoutubeDetailsFromURL(feed.feed, id));
            }else{
                html = generateFeedComponent(generateNewsDetails(feed.feed, id));
            }
            feeds[x].inserted = true;
            $("#note_input").append(html);
            $("#note_input").animate({
                scrollTop: $("#note_input")[0].scrollHeight
            }, 500);
        }
    }
    function generateNewsDetails(data, x){
        return {
            "image": data.urlToImage,
            "title": data.title.slice(0, 30),
            "href": data.url,
            "id": x
        }
    }
    function generateYoutubeDetailsFromURL(data, x){
        let video_id = data.url.split("?v=")[1];
        return {
            "image": "https://i1.ytimg.com/vi/" + video_id + "/hqdefault.jpg",
            "title": data.title,
            "href": data.url,
            "id": x
        }
    }
    function generateSpotifyData(track, x){
        return {
            "image": track.album.images[0].url, 
            "title": track.name,
            "href": track.external_urls.spotify,
            "id": x
        }
    }
    function generateFeedComponent(data, attrs=[], embedMode='feed'){
        
        let html = `<div class="feed row align-items-center" id="feed-` + data.id +`"`;
        for(let attr in attrs){
            let a = attrs[attr];
            html += ` ` + a.key + `=` + a.value +` `;
        }
        html += `>`;
        if(embedMode == 'feed' || embedMode == 'spotify'){
            html += `<div class="col-4">
                        <img src="` + data.image + `" class="img-fluid">
                    </div>
                    <div class="col-8">
                        <a class="title" target="_blank" href="` + data.href + `">` + data.title + `</a>
                    </div>
            `;
        }else if(embedMode == "spotify"){
            // to be implemented in a better way
            html += `
                <iframe src="https://open.spotify.com/embed/track/` + data.id + `" style="width:90%;height:100px;" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
            `;
        }
        
        html += `</div>`;
        return html;
    }

    function loadUserPreference(){
        logTerminal("Loading your preferences...");
        $.ajax({
            url: api_endpoints['get-user-preference'],
            method: 'GET',
            dataType: 'JSON',
            success: function(response){
                if(response.status){
                    if(response.data.categories){
                        let categories = response.data.categories.split(',');
                        for(let x in categories){
                            let category = categories[x];
                            $('.my-category[data-category="'+ category +'"]').addClass('selected');
                        }
                    }
                }
            }
        });
    }
    $(".my-category").on('click', function(e){
        e.preventDefault();
        if($(this).hasClass('selected'))
            $(this).removeClass('selected');
        else
            $(this).addClass('selected');
        saveUserPreference();
    });
    function saveUserPreference(){
        var payload = {
            "key": "categories",
            "value": []
        };
        $(".my-category").each(function(i, v){
            $this = $(v);
            if($this.hasClass('selected'))
                payload.value.push($this.attr('data-category'));
        });
        payload.value = payload.value.join(',');
        $.ajax({
            url: api_endpoints['save-user-preference'],
            method: 'GET',
            dataType: 'JSON',
            data: payload,
            success: function(response){
                if(response.status){
                    logTerminal("Successfully saved preferences...");
                }else{
                    logTerminal("Failed saving preferences :(");
                }
            }
        });
    }

    function init() {
        $("#cameraInitialisePopup").show();
        setInterval(function () {
            loadNextForTerminal();
        }, 1000);

        setClock();
        loadUser();
        loadUserPreference();
        loadFeed();
        GetCameraPermissions();
        $("#cameraInitialisePopup").fadeOut();
        $(video).one('canplay', function () {
            // logTerminal("Starting Mood Detection...");
            startCapturingFrames(startMoodDetection);
        });
    }

    init();