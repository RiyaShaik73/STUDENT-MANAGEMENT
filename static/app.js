document.querySelectorAll(".bar-chart").forEach((chart) => {
    const values = chart.dataset.values.split(",").map(Number);
    const max = Math.max(...values, 1);
    chart.innerHTML = values.map((value, index) => {
        const height = Math.max(14, Math.round((value / max) * 100));
        return `<div class="bar-item"><span style="height:${height}%"></span><b>D${index + 1}</b><em>${value}</em></div>`;
    }).join("");
});

document.querySelectorAll(".line-chart").forEach((chart) => {
    const values = chart.dataset.values.split(",").map(Number);
    const max = Math.max(...values, 100);
    chart.innerHTML = values.map((value, index) => {
        const top = 100 - Math.round((value / max) * 86);
        return `<div class="point" style="left:${index * 18 + 4}%; top:${top}%"><span>${value}%</span></div>`;
    }).join("");
});
