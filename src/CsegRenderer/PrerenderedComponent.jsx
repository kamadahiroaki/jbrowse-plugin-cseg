import React from "react";
import { PrerenderedCanvas } from "@jbrowse/core/ui";

const PrerenderedComponent = (props) => {
  return (
    <div style={{ position: "relative" }}>
      <PrerenderedCanvas {...props} />
    </div>
  );
};

export default PrerenderedComponent;
