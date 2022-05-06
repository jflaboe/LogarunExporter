import React, { useState, useEffect } from 'react';

export default function RequestStatus(props) {
    const [request, setRequest] = useState(null);

    const refresh = (rid) => {
        fetch(process.env.REACT_APP_REQUEST_URL, {
            method: "POST",
            body: JSON.stringify({
                "requestId": rid
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

                setRequest(data.data)
                window.localStorage.setItem("request-" + rid, JSON.stringify(data.data));
            }
        })
    }

    useEffect(() => {
        let requestId = window.localStorage.getItem("lastRequest");
        if (!requestId) {
            window.location.href = "/user"
            return;
        }

        let cachedData = window.localStorage.getItem("request-" + requestId);
        if (cachedData) {
            setRequest(JSON.parse(cachedData));
            return;
        }
        refresh(requestId);
    }, []);
    console.log(request)
    let dates = null;
    if (request) {
        console.log(request.dates)
        dates = [];
        Object.keys(request.dates).forEach((k)=>{
            let v = request.dates[k]
            v.date = k;
            console.log(v)
            dates.push(v)
        });
        console.log(dates)
        dates.sort((a, b) => {
            const d1 = rearrangeDate(a.date);
            const d2 = rearrangeDate(b.date);
            if (d1 < d2) return -1;
            if (d1 > d2) return 1;
            return 0;
        })
        console.log(dates)
    }
    return (
        <React.Fragment>
        <div className="request-status">
            <div className="is-request-complete">
                {request && request.completed && request.completed === dates.length ? "Status: Complete" : "Status: In Progress"}
            </div>
            <div className="refresh" onClick={()=>{refresh(window.localStorage.getItem("lastRequest"))}}>Refresh</div>
        </div>
        <div className="request-dates">
            {dates && dates.map((v, i) => {
                return (<LogarunDayStatus key={v.date} complete={v.Complete} activities={v.Activities} date={v.date} />)
        })}
        </div>  
        </React.Fragment>
        
    )
}

function LogarunDayStatus(props) {
    return (
        <div className='logarun request-date'>
            <div className='request-date-date'>{props.date}</div>
            <div className='request-date-complete'>{props.complete ? "Completed" : "In Queue"}</div>
            {
                props.activities && props.activites.map((v,i) => {
                    return (<StravaActivityLink id={i} key={i} aid={v} />);
                })
            }
        </div>
    )
}

function StravaActivityLink(props) {
    return (<a href={"https://www.strava.com/activities/" + props.aid.toString()}>Activity {props.id}</a>)
}

function rearrangeDate(d) {
    const seps = d.split("/");
    return seps[2] + "/" + seps[0] + "/" + seps[1];
}