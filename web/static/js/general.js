function toDate(timestamp) {
    return (!timestamp) ? null : new Date(timestamp * 1000);
}
function toDateString(time, ver) {
    // ver 0: jp, 1: as
    if (ver === 0) return (!time) ? '尚未更新' : time.toLocaleDateString("ja-JP", {timeZone: 'Japan', hour12: false})
    else return (!time) ? '尚未更新' : time.toLocaleDateString("ja-JP", {timeZone: 'Asia/Taipei', hour12: false})
}
function toDateTimeString(time, ver) {
    // ver 0: jp, 1: as
    if (ver === 0) return (!time) ? '尚未更新' : time.toLocaleString("ja-JP", {timeZone: 'Japan', hour12: false})
    else return (!time) ? '尚未更新' : time.toLocaleString("ja-JP", {timeZone: 'Asia/Taipei', hour12: false})
}

function deleteNull(target) {
    var toDelete = [];
    for (let key in target) {
        if (target[key] === null) toDelete.push(key);
    }
    for (let i in toDelete) delete target[toDelete[i]];
}