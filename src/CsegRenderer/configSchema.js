import { ConfigurationSchema } from "@jbrowse/core/configuration";

export default ConfigurationSchema(
  "CsegRenderer",
  {
    height: {
      type: "number",
      defaultValue: 400,
      description: "the height of the track",
    }
  },
  { explicitlyTyped: true }
);

