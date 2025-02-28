import React from "react";
import { observer } from "mobx-react";
import { readConfObject } from "@jbrowse/core/configuration";

function CsegRenderer(props) {
  const { regions, bpPerPx, height = 400 } = props;
  const region = regions[0];
  const width = (region.end - region.start) / bpPerPx;
  const uri =
    (readConfObject(props.adapterConfig, "base") &&
      readConfObject(props.adapterConfig, "base").uri) ||
    "http://localhost:5000/?cseg=" + region.assemblyName;
  const url = uri + `&ref_name=${region.refName}&start=${region.start}&end=${region.end}&width=${Math.ceil(width)}`;
  console.log("Rendering URL:", url);
  console.log("props:", props);

  return (
    <div style={{
      position: "relative",
      width: Math.ceil(width),
      height: height,
    }}>
      <img
        src={url}
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: '100%',
          height: '100%',
          objectFit: 'fill',
        }}
        alt={`Region ${region.refName}:${region.start}-${region.end}`}
      />
    </div>
  );
}

export default observer(CsegRenderer);

