import mountGraph from "./d3GraphUtils.js"

const globals = {
    vertexPrefix: 'vertex_',
    edgePrefix: 'edge_',
    baseUrl: 'http://localhost:8000',
    startNodeId: undefined,
    endNodeId: undefined,
    visitNodesId: [],
    selectingStart: false,
    selectingEnd: false,
    selectingVisists: false,
    defaultNodeColor: '#1B9C85',
    startNodeColor: '#2e6fd9',
    endNodeColor: '#dc3545',
    visitColor: '#ffc107',
    currentPath: [],
}
 
// FUNCTIONS


// END FUNCTIONS

$(document).ready(() => {
    loading();
    init();
})

$('#selectStart').click(() => {
    cleanSelectingModes();
    globals.selectingStart = true;
})

$('#selectEnd').click(() => {
    cleanSelectingModes();
    globals.selectingEnd = true;
})

$('#selectVisits').click(() => {
    cleanSelectingModes();
    globals.selectingVisists = true;
})

$('#findGreedyRoute').click(() => {
    getGreedyPath();
})

$('#findAStarRouteShortest').click(() => {
    getAstarShortest();
})

$('#findAStarRouteWaitingTime').click(() => {
    getAstarWaitingTime();
})

$('#findAStarRouteAvgSpeed').click(() => {
    getAstarAvgSpeed();
})


$('#startSimulation').click(() => {
    startSimulation();
})

$('#endSimulation').click(() => {
    endSimulation();
})

const initCircleClick = () => {
    $('circle').click(function() {
        let id = $(this).attr('id');
        if (globals.selectingStart) {
            if (globals.startNodeId) {
                $('#' + globals.startNodeId).attr('fill', globals.defaultNodeColor);
            }
            if (id == globals.endNodeId) {
                globals.endNodeId = undefined;
            }
            globals.startNodeId = id;
            $(this).attr('fill', globals.startNodeColor)
        } else if (globals.selectingEnd) {
            if (globals.endNodeId) {
                $('#' + globals.endNodeId).attr('fill', globals.defaultNodeColor);
            }
            if (id == globals.startNodeId) {
                globals.startNodeId = undefined;
            }
            globals.endNodeId = id;
            $(this).attr('fill', globals.endNodeColor)
        } else if (globals.selectingVisists) {
            if (id == globals.endNodeId) {
                globals.endNodeId = undefined;
            }
            if (id == globals.startNodeId) {
                globals.startNodeId = undefined;
            }
            globals.visitNodesId.push(id);
            $(this).attr('fill', globals.visitColor)
        }
    });
}

const cleanSelectingModes = () => {
    globals.selectingEnd = false;
    globals.selectingStart = false;
    globals.selectingVisists = false;
}

const loading = () => {
    $('#loadingSpinner').show();
}

const hideLoading = () => {
    $('#loadingSpinner').hide();
}

const init = async () => {
    let request = getRequest(globals.baseUrl + '/graph');

    mountGraph(await request);
    initCircleClick();
    hideLoading();
}

const getRequest = async (url) => {
    let data = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Access-Control-Allow-Origin': 'http://localhost:5173'
        }
    });

    return await data.json();
}

const getGreedyPath = async () => {
    if (!globals.startNodeId)
    return;
    if (!globals.endNodeId)
        return;

    let startV = globals.startNodeId.replace(globals.vertexPrefix, '');
    let endV = globals.endNodeId.replace(globals.vertexPrefix, '');
    let visits = globals.visitNodesId.map((el) => el.replace(globals.vertexPrefix, ''))
    let url = `${globals.baseUrl}/greedyPath?starting_v=${startV}&ending_v=${endV}&visits=${visits}`
    let resPath = await getRequest(url)//.map((el) => {globals.vertexPrefix + el})
    colorPath(resPath);
}

const getAstarShortest = async () => {
    if (!globals.startNodeId)
    return;
    if (!globals.endNodeId)
        return;

    let startV = globals.startNodeId.replace(globals.vertexPrefix, '');
    let endV = globals.endNodeId.replace(globals.vertexPrefix, '');
    let visits = globals.visitNodesId.map((el) => el.replace(globals.vertexPrefix, ''))
    let url = `${globals.baseUrl}/AStarShortest?starting_v=${startV}&ending_v=${endV}&visits=${visits}`
    let resPath = await getRequest(url)//.map((el) => {globals.vertexPrefix + el})
    colorPath(resPath);
}

const getAstarWaitingTime = async () => {
    if (!globals.startNodeId)
    return;
    if (!globals.endNodeId)
        return;

    let startV = globals.startNodeId.replace(globals.vertexPrefix, '');
    let endV = globals.endNodeId.replace(globals.vertexPrefix, '');
    let visits = globals.visitNodesId.map((el) => el.replace(globals.vertexPrefix, ''))
    let url = `${globals.baseUrl}/AStarWaitingTime?starting_v=${startV}&ending_v=${endV}&visits=${visits}`
    let resPath = await getRequest(url)//.map((el) => {globals.vertexPrefix + el})
    colorPath(resPath);
}

const getAstarAvgSpeed = async () => {
    if (!globals.startNodeId)
    return;
    if (!globals.endNodeId)
        return;

    let startV = globals.startNodeId.replace(globals.vertexPrefix, '');
    let endV = globals.endNodeId.replace(globals.vertexPrefix, '');
    let visits = globals.visitNodesId.map((el) => el.replace(globals.vertexPrefix, ''))
    let url = `${globals.baseUrl}/AStarAvgSpeed?starting_v=${startV}&ending_v=${endV}&visits=${visits}`
    let resPath = await getRequest(url)//.map((el) => {globals.vertexPrefix + el})
    colorPath(resPath);
}

const startSimulation = async () => {
    let url = `${globals.baseUrl}/startSimulation`
    let resPath = await getRequest(url)//.map((el) => {globals.vertexPrefix + el})
}

const endSimulation = async () => {
    let url = `${globals.baseUrl}/closeSimulation`
    let resPath = await getRequest(url)//.map((el) => {globals.vertexPrefix + el})
}

const clearPath = () => {
    globals.currentPath.forEach(element => {
        let edgeEl = $('#' + globals.edgePrefix + element);
        edgeEl.css({
            'stroke': '',
            'stroke-width': ''
        });     
           
    });
}

const colorPath = (path) => {
    clearPath();
    path.forEach(element => {
        let edgeEl = $('#' + globals.edgePrefix + element);
        edgeEl.css(
            {
                'stroke': 'rgb(255, 0, 0)',
                'stroke-width': '5'  
            }
        )
    });
    globals.currentPath = path;
}


