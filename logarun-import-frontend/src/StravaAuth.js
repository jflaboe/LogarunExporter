export default class StravaAuth {

    static isAuthenticated() {
        var storage = window.localStorage;
        if (storage.getItem("code")) {
            if ((new Date()).getTime() - storage.getItem("auth-time") < 60 * 60 * 6) {
                return true
            }
        }
        return false
    }

    static loadAuthFromUrlParameters() {
        const params = new Proxy(new URLSearchParams(window.location.search), {
            get: (searchParams, prop) => searchParams.get(prop),
        });
        var storage = window.localStorage;
        
        if (params.code) {
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
        window.location.href = "https://www.strava.com/oauth/authorize?client_id=29352&redirect_uri=" + window.location.origin + "&response_type=code&scope=activity:write,read";
    }


}