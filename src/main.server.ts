import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app';  // Cambiado de App a AppComponent
import { config } from './app/app.config.server';

const bootstrap = () => bootstrapApplication(AppComponent, config);

export default bootstrap;