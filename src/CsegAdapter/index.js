import {
    ConfigurationSchema,
    readConfObject,
  } from "@jbrowse/core/configuration";
  import { ObservableCreate } from "@jbrowse/core/util/rxjs";
  import { BaseFeatureDataAdapter } from "@jbrowse/core/data_adapters/BaseAdapter";

  console.log("adapter")
  
  export const configSchema = ConfigurationSchema(
    "CsegAdapter",
    {
      base: {
        type: "fileLocation",
        description: "base URL for the CSEG API",
        defaultValue: {
          uri: "http://localhost:5000/",
        },
      },
      track: {
        type: "string",
        description: "the additional parameters to pass cseg",
        defaultValue: "",
      },
    },
    { explicitlyTyped: true, explicitIdentifier: "CsegAdapterId" },
  );
  
  export class AdapterClass extends BaseFeatureDataAdapter {
    // console.log("config:",config)
    constructor(config) {
      super(config);
      this.config = config;
    }

    // console.log("region:",region)

    getFeatures(region) {
      console.log("region2:",region)

      const { assemblyName, start, end, refName } = region;
      return ObservableCreate(async observer => {
        const { uri } = readConfObject(this.config, "base");
        const track = readConfObject(this.config, "track");
        observer.complete();
      });
    }
  
    async getRefNames() {
      const arr = [];
      for (let i = 0; i < 23; i++) {
        arr.push(`chr${i}`);
      }
      return arr;
    }
  
    freeResources() {}
  }