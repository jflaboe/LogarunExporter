import React, { useState, useEffect } from 'react';

export default function SiteStats(props) {
    const [siteData, setSiteData] = useState(null);
    useEffect(() =>{
        fetch(process.env.REACT_APP_REQUEST_URL, {
            method: "POST",
            body: JSON.stringify({
                "test": "test"
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

                setSiteData(data.data)
                window.localStorage.setItem("request-" + rid, JSON.stringify(data.data));
            }
        });
    }, [])
}