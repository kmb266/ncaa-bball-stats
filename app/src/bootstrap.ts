import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { enableProdMode } from '@angular/core';
import { AppModule }  from './app.component';
enableProdMode();
platformBrowserDynamic().bootstrapModule(AppModule);
