import StravaAuth from './StravaAuth';
import React, { useEffect, useState } from 'react';
import './StravaLogin.css';

export default function StravaLogin(props) {
    StravaAuth.loadAuthFromUrlParameters();
    if (StravaAuth.isAuthenticated()) {
        return (
            <React.Fragment></React.Fragment>
        );
    }

    return (
        <div className="login-container">
            <div className="login-modal">
                <div className="login-modal-text">
                    You must be logged in to Strava to use this site. The site will ask for access so that it can post to Strava on your behalf.
                </div>
                <button className="login-modal-button site-button" onClick={StravaAuth.redirectToAuth}>
                    Login to Strava
                </button>
            </div>
        </div>
    )
}