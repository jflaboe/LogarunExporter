import { useEffect, useState } from 'react';
import StravaAuth from './StravaAuth';

export default function UserInfo(props) {
    const [userInfo, setUserInfo] = useState(null);

    const refresh = () => {
        var authData = StravaAuth.getAuthData();
        fetch(process.env.REACT_APP_USER_URL, {
            method: "POST",
            body: JSON.stringify({
                "accessToken": authData.code
            })
        })
        .then(function(response) {
            if (!response.ok) {
                console.log(response)
            }
            return response.json()
        }).then(data => {
            if (data.success) {
                console.log(data)
                window.localStorage.setItem("userinfo", JSON.stringify(data.data))
                setUserInfo(data.data)
            }
        })
    }

    useEffect(() => {
        
        let cachedData = window.localStorage.getItem("userinfo");
        if (cachedData) {
            setUserInfo(JSON.parse(cachedData));
            return;
        }
        refresh();
    }, []);

    if (userInfo) {
        let requests = userInfo.requests;
        return (
            <div>
                {requests && requests.length > 0 && requests.map((request) => {
                    return (
                        <RequestSummary request={request} key={request.rid} />
                    );
                })}
            </div>
        )
    }
    return (
        <div>Loading...</div>
    )
}

function RequestSummary(props) {
    return (
        <div className="request-summary" onClick={()=>{redirectToRequest(props.request.rid)}}>
            <div className="dates">{props.request.start + " to " + props.request.end}</div>
            <div className="is-complete">{props.request.complete ? "Status: Complete" : "Status: In Progress"}</div>
        </div>
    )
}

function redirectToRequest(rid) {
    window.localStorage.setItem("lastRequest", rid);
    window.location.href = "/request";
}