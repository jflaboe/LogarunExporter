import React, { useEffect, useState } from 'react';
import './Menu.css';

export default function Menu(props) {
    const [isOpen, setIsOpen] = useState(false);
    let menuClass = "menu-links";
    const goTo = function(path) {
        window.location.href = path;
    }
    return (
        <div className="menu">
            <div className="menu-button logarun" onClick={()=>{setIsOpen(!isOpen); console.log(isOpen)}}>
                Menu
            </div>
            {isOpen &&
            <div className="menu-links">
                <div className="menu-link" onClick={()=>goTo('/')}>
                    Request Import
                </div>
                <div className="menu-link" onClick={()=>goTo('/user')}>
                    Your Requests
                </div>
                <div className="menu-link" onClick={()=>goTo('/request')}>
                    Most Recent Request
                </div>
            </div> }
        </div>
        
    );
}