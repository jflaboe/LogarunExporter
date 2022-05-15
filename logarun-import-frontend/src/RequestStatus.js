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
        console.log("update");
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
    let dates = null;
    if (request) {
        dates = [];
        Object.keys(request.dates).forEach((k)=>{
            let v = request.dates[k]
            v.date = k;
            dates.push(v)
        });
        dates.sort((a, b) => {
            const d1 = rearrangeDate(a.date);
            const d2 = rearrangeDate(b.date);
            if (d1 < d2) return -1;
            if (d1 > d2) return 1;
            return 0;
        })
    }
    let daysComplete = 0;
    let distanceComplete = 0;
    let activitiesComplete = 0;

    if (dates !== null) {
        daysComplete = dates.reduce((prev, current) => {
            if (current.Complete) {
                return prev + 1;
            }
            return prev;
        }, 0);
    
        distanceComplete = dates.reduce((prev, current) => {
            if (current.Complete) {
                return prev + current.Distance;
            }
            return prev;
        }, 0);
    
        activitiesComplete = dates.reduce((prev, current) => {
            if (current.Complete) {
                return prev + current.Activities;
            }
            return prev;
        }, 0);
    }
    
    
    return (
        <React.Fragment>
        <div className="request-status">
            <div className="is-request-complete">
                {request && request.complete && request.completed === dates.length ? "Status: Complete" : "Status: In Progress"}
            </div>
            <div>{daysComplete} / {request ? dates.length : 0} days complete</div>
            <div>{(distanceComplete / 1609).toFixed(2)} Miles Uploaded</div>
            <div>{activitiesComplete} Activities Uploaded</div>
            <button className="refresh site-button" onClick={()=>{refresh(window.localStorage.getItem("lastRequest"))}}>Refresh</button>
        </div>
        <div className="request-dates">
            {dates && dates.map((v, i) => {
                return (<LogarunDayStatus key={v.date} complete={v.Complete} activities={v.Activities} date={v.date} distance={v.Distance} />)
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
            {props.complete && 
            <div className="request-date-data">
                <div className='request-date-activities'>Activities Uploaded: {props.activities}</div>
                <div className='request-date-distance'>Distance Uploaded: {(props.distance/1609.0).toFixed(2)} miles</div>
            </div>
            }
        </div>
    )
}

function StravaActivityLink(props) {
    return (<div></div>);
    return (<a href={"https://www.strava.com/activities/" + props.aid.toString()}>Activity {props.id}</a>)
}

function rearrangeDate(d) {
    const seps = d.split("/");
    return seps[2] + "/" + seps[0] + "/" + seps[1];
}