export default class StravaAuth {

    static isAuthenticated() {
        var storage = window.localStorage;
        if (storage.getItem("code") !== null) {
            if ((new Date()).getTime() - storage.getItem("auth-time") < 60 * 60 * 1000 * 6) {
                return true
            }
        }
        console.log(storage.getItem("code"));
        console.log("not logged in");
        return false
    }

    static loadAuthFromUrlParameters() {
        const getParams = function() {
            let search = window.location.search;
            if (search.length < 1) {
                return {};
            }

            let items = search.substring(1).split("&").reduce((prev, cur) => {
                let vals = cur.split("=");
                prev[vals[0]] = vals[1];
                return prev;
            }, {})

            return items;
        }
        const params = getParams();
        var storage = window.localStorage;
        
        if (params.code) {
            console.log("Parameters Found, setting correct url");
            storage.setItem("code", params.code)
            storage.setItem("auth-time", (new Date()).getTime())
            let newurl = window.location.protocol + "//" + window.location.host + window.location.pathname;
            window.history.pushState({path:newurl},'',newurl);
        }
        
    }

    static getAuthData() {
        var storage = window.localStorage;
        return {
            "code": storage.getItem("code"),
            "expiryStart": storage.getItem("auth-time")
        }
    }

    static redirectToAuth() {
        window.location.href = "https://www.strava.com/oauth/authorize?client_id=29352&redirect_uri=" + window.location.href + "&response_type=code&scope=activity:write,read";
    }


}