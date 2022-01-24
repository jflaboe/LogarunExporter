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
        }
        
    }

    static getAuthData() {
        var storage = window.localStorage;
        return {
            "code": storage.getItem("code"),
            "expiryStart": storage.getItem("auth-time")
        }
    }


}