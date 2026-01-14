import React from 'react';
import { IThemeManager, ReactWidget } from '@jupyterlab/apputils';
import { IStateDB } from '@jupyterlab/statedb';
import { PLUGIN_NAMESPACE } from '.';
import { requestAPI } from './handler';
import JupyterIGV from 'jupyter-igv-component';
import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';

export class JupyterIGVWidget extends ReactWidget {
  constructor(
    themeManager: IThemeManager,
    version: string,
    name: string,
    stateDB: IStateDB,
    stateKeyPrefix: string,
    initialState?: Map<string, any>
  ) {
    super();
    this.themeManager = themeManager;
    this.bsTheme = this.setBSTheme(this.themeManager.theme);
    this.version = version;
    this.name = name;
    this._stateDB = stateDB;
    this._stateKeyPrefix = stateKeyPrefix;
    this._cache = initialState ?? new Map<string, any>();

    // Add class for the widget
    this.addClass('jupyter-igv-widget');

    // Cleanup stateDB on widget disposal
    this.disposed.connect(this._cleanup, this);
  }

  themeManager: IThemeManager;
  bsTheme: string;
  version: string;
  name: string;
  private _stateDB: IStateDB;
  private _stateKeyPrefix: string;
  private _cache: Map<string, any>;

  // Resize IGV on widget resize
  protected onResize(msg: Widget.ResizeMessage): void {
    super.onResize(msg);
    window.dispatchEvent(new Event('resize'));
  }

  // Trigger widget re-render on show
  protected onAfterShow(msg: Message): void {
    super.onAfterShow(msg);
    setTimeout(() => this.update(), 500);
  }

  // Save value to stateDB
  private _save(stateKey: string, value: any) {
    this._stateDB.save(stateKey, value).catch(error => {
      console.error(`Failed to save state ${stateKey}:`, error);
    });
  }

  // Cleanup stateDB
  private async _cleanup() {
    const pluginStateKeys = await this._stateDB.list(PLUGIN_NAMESPACE);

    // Remove all keys that start with the stateKeyPrefix
    pluginStateKeys.ids.forEach(stateKey => {
      if (stateKey.startsWith(this._stateKeyPrefix)) {
        this._stateDB.remove(stateKey).catch(error => {
          console.error(`Failed to remove state ${stateKey}:`, error);
        });
      }
    });
  }

  // Set the bootstrap theme from JupyterLab theme
  setBSTheme(theme: string | null): string {
    this.bsTheme =
      theme && !this.themeManager.isLight(theme) ? 'dark' : 'light';
    document.documentElement.setAttribute('data-bs-theme', this.bsTheme);
    return this.bsTheme;
  }

  // Update the bootstrap theme and re-render widget
  updateTheme(theme: string | null): void {
    this.setBSTheme(theme);
    this.update();
  }

  // Handler for generating presigned S3 URLs
  s3PresignHandler = async (uri: string): Promise<string> => {
    const data = await requestAPI<any>('s3-presign', {}, ['uri', uri]);
    return data['url'];
  };

  // Get item from the cache
  getItem = (key: string) => {
    const stateKey = `${this._stateKeyPrefix}:${key}`;
    return this._cache.get(stateKey);
  };

  // Set item in the cache and save to stateDB
  setItem = (key: string, value: any) => {
    const stateKey = `${this._stateKeyPrefix}:${key}`;
    this._cache.set(stateKey, value);
    this._save(stateKey, value);
  };

  // Set the title of the widget
  setTitle = (title: string): void => {
    this.title.label = title;
  };

  render(): JSX.Element {
    // Any hidden JupyterIGV instances are disabled until viewing
    // This prevents hidden tabs from initialising IGV with a width and height of 0
    return (
      <JupyterIGV
        enabled={this.node.clientWidth > 0}
        version={this.version}
        s3PresignHandler={this.s3PresignHandler}
        setItem={this.setItem}
        getItem={this.getItem}
        setTitle={this.setTitle}
      />
    );
  }
}

export default JupyterIGVWidget;
