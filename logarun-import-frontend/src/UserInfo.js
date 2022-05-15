import { useEffect, useState } from 'react';
import StravaAuth from './StravaAuth';

export default function UserInfo(props) {
    const [userInfo, setUserInfo] = useState(null);

    const refresh = () => {
        var authData = StravaAuth.getAuthData();
        fetch(process.env.REACT_APP_USER_URL, {
            method: "POST",
            body: JSON.stringify({
                "accessToken": authData.code,
                "sid": window.localStorage.getItem("sid")
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
        refresh();
    }, []);

    if (userInfo) {
        let requests = userInfo.requests;
        return (
            <div className="user-info">
                <div className="user-info-summary">
                    <div>Activities Uploaded: {userInfo.activities}</div>
                    <div>Miles Uploaded: {(userInfo.distance/1609).toFixed(2)}</div>
                </div>
                <div className="user-info-requests">
                    <div className="user-info-requests-title">
                        Your Requests:
                    </div>
                    {requests && Object.keys(requests).length > 0 && Object.keys(requests).map((requestId) => {
                        return (
                            <RequestSummary request={requests[requestId]} key={requestId} id={requestId} />
                        );
                    })}
                </div>
                
            </div>
        )
    }
    return (
        <div>Loading...</div>
    )
}

function RequestSummary(props) {
    return (
        <div className="request-summary logarun" onClick={()=>{redirectToRequest(props.id)}}>
            <div className="dates">{props.request.start + " to " + props.request.end}</div>
            <div className="is-complete">{props.request.completed >= props.request.days ? "Status: Complete" : "Status: In Progress"}</div>
        </div>
    )
}

function redirectToRequest(rid) {
    window.localStorage.setItem("lastRequest", rid);
    window.location.href = "/request";
}