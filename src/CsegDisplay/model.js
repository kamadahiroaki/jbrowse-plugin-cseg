import { types } from 'mobx-state-tree'
import {
  // AnyConfigurationSchemaType,
  ConfigurationReference,
} from '@jbrowse/core/configuration'
import { getParentRenderProps } from '@jbrowse/core/util/tracks'

console.log("model.js")

export default (pluginManager,configSchema) => {
  console.log("pluginManager:model.js", pluginManager)

  const { BaseLinearDisplay } = (
    pluginManager.getPlugin('LinearGenomeViewPlugin')
  )?.exports

  console.log('BaseLinearDisplay', BaseLinearDisplay);

  return types
    .compose(
      'CsegDisplay',
      BaseLinearDisplay,
      types.model({
        type: types.literal('CsegDisplay'),
        configuration: ConfigurationReference(configSchema),
      }),
    )
    .views(self => {
      const {
        renderProps: superRenderProps,
        trackMenuItems: superTrackMenuItems,
      } = self

      return {
        get rendererTypeName() {
          return 'CsegRenderer'  // 重要: これがレンダラーの名前と一致している必要がある
        },

        renderProps() {
          return {
            ...superRenderProps(),
            ...getParentRenderProps(self),
            displayModel: self,
            config: self.configuration.renderer,
          }
        },

        // trackMenuItems() {
        //   return [
        //     ...superTrackMenuItems(),
        //     // 必要に応じてメニュー項目を追加
        //   ]
        // },
      }
    })
}