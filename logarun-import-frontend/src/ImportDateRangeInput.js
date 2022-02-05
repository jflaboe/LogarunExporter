import { useState } from 'react';
import DatePicker from "react-datepicker";
import StravaAuth from './StravaAuth';

import "react-datepicker/dist/react-datepicker.css";

export default function ImportDateRangeInput(props) {
    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date());
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("")
    const [loadingImport, setLoadingImport] = useState(false);
    const [email, setEmail] = useState("");
    const [help, setHelp] = useState("");
    const [askedForHelp, setAskedForHelp] = useState(false);
    const [defaultTitle, setDefaultTitle] = useState("Imported from Logarun");
    const [useDefaultTitle, setUseDefaultTitle] = useState(false);
    const [useWatermark, setUseWaterMark] = useState(false);

    const startImport = () => {
        setLoadingImport(true);
        var authData = StravaAuth.getAuthData();
        fetch(process.env.REACT_APP_IMPORT_URL, {
            method: "POST",
            body: JSON.stringify({
                "username": username,
                "password": password,
                "startDate": startDate.toLocaleDateString('en-US'),
                "endDate": endDate.toLocaleDateString('en-US'),
                "useDefaultTitle": useDefaultTitle,
                "defaultTitle": defaultTitle,
                "useWatermark": useWatermark,
                "accessToken": authData.code,
                "tokenExpiryStart": authData.expiryStart
            })
        }).then(function(response) {
            if (!response.ok) {
                console.log(response)
                setLoadingImport(false)
            }
            return response.json()
        }).then(data => {
            if (data.success) {
                console.log("succeeded")
            } else {
                if (data.reason === "strava-account-verification-failed") {
                    StravaAuth.redirectToAuth();
                }
            }
        })
    }

    const getHelp = () => {
        setAskedForHelp(true);
        fetch(process.env.REACT_APP_HELP_URL, {
            method: "POST",
            body: JSON.stringify({
                "email": email,
                "help": help
            })

        })

    }
    const updateField = (event) => {
        console.log(event.target)
        if (event.target.name === "password") {
            setPassword(event.target.value)
        }

        if (event.target.name === "username") {
            setUsername(event.target.value)
        }

        if (event.target.name === "email") {
            setEmail(event.target.value)
        }

        if (event.target.name === "help") {
            setHelp(event.target.value)
        }

        if (event.target.name === "useDefaultTitle") {
            setUseDefaultTitle(event.target.checked)
        }

        if (event.target.name === "defaultTitle") {
            setDefaultTitle(event.target.value)
        }

        if (event.target.name === "useWatermark") {
            setUseWaterMark(event.target.checked)
        }
    }
    return (
        <div className="logarun-import">
            <div className="logarun-import-form logarun">
                <div className="import-form-username import-form-text">
                    <div className={username === "" ? "error" : ""}>Logarun Username</div>
                    <div>
                        <input type="text"name="username" value={username} onChange={updateField} />
                    </div>
                </div>
                <div className="import-form-password import-form-text">
                    <div>Logarun Password (Optional)</div>
                    <div>
                        <input type="text" name="password" value={password} onChange={updateField} />
                    </div>
                </div>
                <div className="import-form-start import-form-text">
                    <div>Start Date</div>
                    <div>
                        <DatePicker  selected={startDate} onChange={(date) => setStartDate(date)} />
                    </div>
                    
                </div>
                <div className="import-form-end import-form-text">
                    <div>End Date</div>
                    <div>
                        <DatePicker selected={endDate} onChange={(date) => setEndDate(date)} />
                    </div>
                    
                </div>
                <div className="import-form-text">
                    <div>Use a default title (when none present)?</div>
                    <div>
                        <input type="checkbox" name="useDefaultTitle" value={useDefaultTitle} onChange={updateField} />
                    </div>
                    
                </div>
                <div className="import-form-text">
                    <div>Default Title</div>
                    <div>
                        <input disabled={!useDefaultTitle} type="text" name="defaultTitle" value={defaultTitle} onChange={updateField} />
                    </div>
                </div>
                <div className="import-form-text">
                    <div>Add "(Imported from Logarun)" to the description</div>
                    <div>
                        <input type="checkbox" name="useWatermark" value={useDefaultTitle} onChange={updateField} />
                    </div>
                    
                </div>
                <div className="import-form-button">
                    <button disabled={loadingImport} onClick={startImport}>Start Import</button>
                </div>
                
            </div>
            <div className="logarun-import-form-explain logarun">
                
                <h3>How to use</h3>
                <p>Enter your username and password (only if your account is private) and choose the start/end date for the migration. Right now, it is setup to migrate all run/swim/bike data.</p>
                <h3>FAQ</h3>
                <p>Q: How long will it take to migrate?</p>
                <p>A: Depends on how many are using the site. The tool can pull about ten records at a time for a total average of one record per second without degrading the performance of Logarun, so expect 6-10 minutes per year of data.</p>
                <br />
                <p>Q: Will the tool save my run titles?</p>
                <p>A: Yes. If there are more than one activities in a day, the corresponding Strava activities will have the same title.</p>
                <br />
                <p>Q: Will the tool copy run description?</p>
                <p>A: Yes.</p>
                <br />
                <p>Q: Will the tool copy comments?</p>
                <p>A: No.</p>
                <br />
                <p>Q: What activites will be migrated?</p>
                <p>A: Running, biking, and swimming. For more activites, please contact me using the form below.</p>
                <h3>About</h3>
                <p>I created this as a means to migrate my own data from Logarun to Strava, but decided to make a little project out of it and make it a publicly available tool. As much as I loved using Logarun, it's time to move your data before it's lost to the void. As homage to our beloved site, I've made the styling here the same.</p>
                <a href="https://www.logarun.com/report.aspx?username=jflaboe&type=General">John's Logarun</a><br/>
                <a href="https://www.strava.com/athletes/28384877">John's Strava</a>
                <h3>Contact</h3>
                If you have questions, are having issues, or have a request, please feel free to fill in your contact information below and I will get back to you soon.
                <div className="logarun-import-form">
                    <div className="import-form-email import-form-text">
                        <div>Email</div>
                        <div>
                            <input type="text"name="email" value={email} onChange={updateField} />
                        </div>
                    </div>
                    <div className="import-form-email import-form-text">
                        <div>How can I help?</div>
                        <div>
                            <textarea id="help" rows="5" name="help" value={help} onChange={updateField} />
                        </div>
                    </div>
                    <div id="help-button" className="import-form-button">
                        <button disabled={askedForHelp} onClick={getHelp}>Send</button>
                    </div>
                </div>
                
            </div>
        </div>
        
    )
}