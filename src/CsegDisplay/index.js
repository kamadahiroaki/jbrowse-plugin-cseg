import configSchemaF from './configSchema'
import modelF from './model'

console.log("CsegDisplay/index.js")

export default (pluginManager) => {
  console.log("csegdisplay.index.js pluginManager:", pluginManager)
  const schema = configSchemaF(pluginManager)
  return {
    configSchema: schema,
    stateModel: modelF(pluginManager, schema),
  }
}

