// import PluginManager from '@jbrowse/core/PluginManager'
import { ConfigurationSchema } from '@jbrowse/core/configuration'

console.log("configSchema.js")

export default pluginManager => {
  console.log("pluginManager:configSchema.js", pluginManager)
  const { baseLinearDisplayConfigSchema } = pluginManager.getPlugin('LinearGenomeViewPlugin').exports
  return ConfigurationSchema(
    'CsegDisplay',
    { renderer: pluginManager.pluggableConfigSchemaType('renderer'),},
    { baseConfiguration: baseLinearDisplayConfigSchema, explicitlyTyped: true },
  )
}