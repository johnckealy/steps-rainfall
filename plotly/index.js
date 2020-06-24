async function fetchAsync() {
    let data = await (await fetch('../radar.json')).json();
    return data;
}

const colorScale = [
    [0, 'rgb(255,255,255)'],
    [0.25, 'rgb(31,120,180)'],
    [0.45, 'rgb(178,223,138)'],
    [0.65, 'rgb(51,160,44)'],
    [0.85, 'rgb(178,44,255)'],
    [1, 'rgb(218,218,217)']
]

fetchAsync().then(radarData => {

    const data = [{
        z: radarData,
        type: 'contour',
        colorscale: colorScale,
        contours: {
            coloring: 'heatmap'
          }
    }];

    const layout = {
        title: 'Basic Contour Plot'
    }

    Plotly.newPlot('myDiv', data, layout);
})