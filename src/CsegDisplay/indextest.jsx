// import React from 'react'
// import { observer } from 'mobx-react'

// const CsegDisplay = observer(({ model }) => {
//     console.log("CsegDisplay model:", model) // ✅ ここで model の情報を確認
//     const { imageURL } = model.configuration
//     const region = model.displayedRegions[0]
//     const { refName, start, end } = region || {}

//     // 画像 URL を作成
//     const imgSrc = imageURL.value
//         .replace("{refName}", refName || "")
//         .replace("{start}", start?.toString() || "0")
//         .replace("{end}", end?.toString() || "1000")

//     return (
//         <div>
//             <h3>Cseg Track</h3>
//             <img src={imgSrc} alt="CSEG visualization" style={{ width: '100%' }} />
//         </div>
//     )
// })

// export default CsegDisplay
