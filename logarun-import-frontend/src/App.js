import logo from './logo.gif';
import StravaAuth from './StravaAuth';
import './App.css';
import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ImportDateRangeInput from './ImportDateRangeInput';

function App() {
  
  useEffect(()=>{
    StravaAuth.loadAuthFromUrlParameters()
    if (!StravaAuth.isAuthenticated()) {
      window.location.href = "https://www.strava.com/oauth/authorize?client_id=29352&redirect_uri=" + window.location.origin + "&response_type=code&scope=activity:write,read";
    }
  }, []);
  
  return (
    <div className="App">
      <div className="header">
        <div className="header-logarun-logo">
          <img src="https://www.logarun.com/v5.2/s/Green/logo.gif" />
        </div>
        <div className="header-strava-logo">
          <img src="https://iconape.com/wp-content/files/jg/99203/png/strava-2.png" />
        </div>
      </div>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ImportDateRangeInput />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
