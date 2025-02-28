import Plugin from '@jbrowse/core/Plugin'
import PluginManager from '@jbrowse/core/PluginManager'
// import ViewType from '@jbrowse/core/pluggableElementTypes/ViewType'
import AdapterType from '@jbrowse/core/pluggableElementTypes/AdapterType'
// import { AbstractSessionModel, isAbstractMenuManager } from '@jbrowse/core/util'
import { version } from '../package.json'
// import {
//   ReactComponent as HelloViewReactComponent,
//   stateModel as helloViewStateModel,
// } from './HelloView'
// import { observer } from 'mobx-react'
import { ConfigurationSchema } from '@jbrowse/core/configuration'

import {configSchema as CsegAdapterConfigSchema, AdapterClass as CsegAdapterClass} from './CsegAdapter'
// import { CsegAdapter } from './CsegAdapter'

import TrackType from '@jbrowse/core/pluggableElementTypes/TrackType'
// import { types } from 'mobx-state-tree'
// import { LinearBasicDisplay } from '@jbrowse/plugin-linear-genome-view'
import CsegDisplayF from './CsegDisplay'
import { DisplayType } from '@jbrowse/core/pluggableElementTypes'
// import {BaseLinearDisplay, BaseLinearDisplayComponent } from '@jbrowse/plugin-linear-genome-view'

console.log("CsegPluginbefore");
// import BoxRendererType from '@jbrowse/core/pluggableElementTypes/renderers/BoxRendererType'
// import * as BoxRendererModule from "@jbrowse/core/pluggableElementTypes/renderers/BoxRendererType";
// const { default: BoxRendererType } = BoxRendererModule;

import CsegRenderer from "./CsegRenderer";
import { configSchema as CsegRendererConfigSchema } from "./CsegRenderer";

// console.log("BoxRendererType:",BoxRendererType)
// console.log("BoxRendererType.default:",BoxRendererType.default)

import {
  createBaseTrackConfig,
  createBaseTrackModel,
} from '@jbrowse/core/pluggableElementTypes/models'

import {ServerSideRendererType} from '@jbrowse/core/pluggableElementTypes'

export default class CsegPlugin extends Plugin {
  name = 'CsegPlugin' 
  version = version

  install(pluginManager:PluginManager){
    const LGVPlugin = pluginManager.getPlugin(
      'LinearGenomeViewPlugin',
    ) as unknown as import('@jbrowse/plugin-linear-genome-view').default
    const { BaseLinearDisplayComponent } = LGVPlugin.exports
    console.log("BaseLinearDisplayComponent",BaseLinearDisplayComponent);


    pluginManager.addAdapterType(() => {
      console.log("addCsegAdapter");
      return new AdapterType({
        name: 'CsegAdapter',
        configSchema: CsegAdapterConfigSchema,
        AdapterClass: CsegAdapterClass,
      })
    })
  
    pluginManager.addTrackType(() => {
      console.log("addCSEGTrack");
  
      const configSchema = ConfigurationSchema(
        'CSEGTrack',
        {
                // トラックの設定オプションを定義
                // renderer: {
                //   type: 'stringEnum',
                //   model: types.enumeration('Renderer', ['CsegRenderer']),
                //   defaultValue: 'CsegRenderer',
                // },
        },
        {
          baseConfiguration: createBaseTrackConfig(pluginManager),
          explicitIdentifier: 'trackId',
        },
      )
      return new TrackType({
        name: 'CSEGTrack',
        configSchema,
        stateModel: createBaseTrackModel(
          pluginManager,
          'CSEGTrack',
          configSchema,
        ),
      })
    })
  
  
  


  pluginManager.addRendererType(() => {
    // const { BoxRendererType } = pluginManager.lib['@jbrowse/core/pluggableElementTypes/renderers']
    // return new BoxRendererType({
      // const { RendererType } = pluginManager.lib['@jbrowse/core/pluggableElementTypes']
      // return new RendererType({
    // return new CsegRendererType({
    return new ServerSideRendererType({
      name: 'CsegRenderer',
      ReactComponent: CsegRenderer,
      configSchema: CsegRendererConfigSchema,
      pluginManager,
    })
  })


      pluginManager.addDisplayType(() => {
        console.log("addCsegDisplay");
      // const {configSchema,stateModel}=pluginManager.load(CsegDisplay);
      const {configSchema,stateModel}=CsegDisplayF(pluginManager);
      return new DisplayType({
        name: 'CsegDisplay',
        configSchema,
        stateModel,
        trackType: 'CSEGTrack',
        viewType: 'LinearGenomeView',
        ReactComponent: BaseLinearDisplayComponent,
      })
    })
    

    //   pluginManager.addViewType(() => {
    //     console.log("addViewType");
    //   return new ViewType({
    //     name: 'HelloView',
    //     stateModel: helloViewStateModel,
    //     ReactComponent: HelloViewReactComponent,
    //   })
    // })
  }
}


