const API_BASE = "/api";

const statusBox = document.getElementById("status");
const optimizeBtn = document.getElementById("optimizeBtn");

const resultsSection = document.getElementById("results");
const routeSection = document.getElementById("routeSection");
const timeline = document.getElementById("routeTimeline");

const naiveTimeEl = document.getElementById("naiveTime");
const optimizedTimeEl = document.getElementById("optimizedTime");
const improvementEl = document.getElementById("improvementPct");

let map = L.map("map").setView([28.6129, 77.2295], 14);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

let nodeMarkers = {};
let routeLine = null;

async function loadStopCandidates() {

    try {

        const res = await fetch(`${API_BASE}/stop-candidates`);
        const nodes = await res.json();

        const select = document.getElementById("stopsSelect");

        nodes.forEach(node => {

            const option = document.createElement("option");
            option.value = node.node_id;
            option.textContent = `Node ${node.node_id}`;

            select.appendChild(option);

            const marker = L.circleMarker([node.lat, node.lng], {

                radius:6,

                color:"#3b82f6",

                fillColor:"#3b82f6",

                fillOpacity:.85

            }).addTo(map);

            marker.bindPopup(`Node ${node.node_id}`);

            nodeMarkers[node.node_id] = {

                marker,

                lat:node.lat,

                lng:node.lng

            };

        });

    }

    catch(err){

        statusBox.textContent="Unable to load stop candidates.";

    }

}

function getSelectedStops(){

    const select=document.getElementById("stopsSelect");

    return [...select.selectedOptions].map(x=>parseInt(x.value));

}

function sleep(ms){

    return new Promise(resolve=>setTimeout(resolve,ms));

}

async function showLoading(){

    const messages=[

        "Loading road network...",

        "Running A* Search...",

        "Building distance matrix...",

        "Applying Nearest Neighbor...",

        "Improving route with 2-Opt..."

    ];

    for(const msg of messages){

        statusBox.textContent=msg;

        await sleep(350);

    }

}

function animateNumber(element,target,suffix){

    let start=0;

    const duration=800;

    const increment=target/(duration/16);

    const timer=setInterval(()=>{

        start+=increment;

        if(start>=target){

            clearInterval(timer);

            element.textContent=target.toFixed(1)+suffix;

        }

        else{

            element.textContent=start.toFixed(1)+suffix;

        }

    },16);

}

function buildTimeline(route){

    timeline.innerHTML="";

    route.forEach((node,index)=>{

        const item=document.createElement("div");
        item.className="timeline-item";

        item.innerHTML=`

            <div class="timeline-number">

                ${index+1}

            </div>

            <div class="timeline-content">

                <h3>Node ${node}</h3>

                <p>Visit Stop ${index+1}</p>

            </div>

        `;

        timeline.appendChild(item);

        if(index!==route.length-1){

            const arrow=document.createElement("div");

            arrow.className="timeline-arrow";

            arrow.innerHTML="➜";

            timeline.appendChild(arrow);

        }

    });

}

function drawRoute(route){

    if(routeLine){

        map.removeLayer(routeLine);

    }

    const latlngs=[];

    route.forEach(id=>{

        if(nodeMarkers[id]){

            latlngs.push([

                nodeMarkers[id].lat,

                nodeMarkers[id].lng

            ]);

        }

    });

    routeLine=L.polyline(latlngs,{

        color:"#3b82f6",

        weight:5,

        opacity:.9

    }).addTo(map);

    map.fitBounds(routeLine.getBounds(),{

        padding:[40,40]

    });

    route.forEach((id,index)=>{

        nodeMarkers[id].marker.bindPopup(

            `Stop ${index+1}<br>Node ${id}`

        );

    });

}

async function optimizeRoute(){

    const stops=getSelectedStops();

    if(stops.length<2){

        alert("Please select at least two stops.");

        return;

    }

    optimizeBtn.disabled=true;

    optimizeBtn.textContent="Optimizing...";

    await showLoading();

    const payload={

        stops,

        day_type:document.getElementById("dayType").value,

        hour:parseInt(document.getElementById("hour").value)

    };

    try{

        const res=await fetch(`${API_BASE}/optimize-route`,{

            method:"POST",

            headers:{

                "Content-Type":"application/json"

            },

            body:JSON.stringify(payload)

        });

        const data=await res.json();

        if(data.error){

            throw new Error(data.error);

        }

        resultsSection.classList.remove("hidden");

        routeSection.classList.remove("hidden");

        animateNumber(

            naiveTimeEl,

            data.naive_time_sec/60,

            " min"

        );

        animateNumber(

            optimizedTimeEl,

            data.optimized_time_sec/60,

            " min"

        );

        animateNumber(

            improvementEl,

            data.improvement_pct,

            "%"

        );

        buildTimeline(data.optimized_order);

        drawRoute(data.optimized_order);

        statusBox.textContent="Optimization Complete ✓";

    }

    catch(err){

        console.error(err);

        alert(err.message);

        statusBox.textContent="Optimization Failed";

    }

    finally{

        optimizeBtn.disabled=false;

        optimizeBtn.textContent="Optimize Route";

    }

}

optimizeBtn.addEventListener(

    "click",

    optimizeRoute

);

loadStopCandidates();