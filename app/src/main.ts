import {Aurelia} from 'aurelia-framework'
import environment from './environment';
import {PLATFORM} from 'aurelia-pal';
import 'aurelia-materialize-bridge';
import 'materialize-css';
// import '../static/styles.css';

export function configure(aurelia: Aurelia) {
    aurelia.use
        .standardConfiguration()
        .plugin(PLATFORM.moduleName('aurelia-materialize-bridge'), b => b.useAll())
        .feature(PLATFORM.moduleName('resources/index'))
        .plugin(PLATFORM.moduleName('@krisdages/aurelia-table'));

  // Uncomment the line below to enable animation.
  // aurelia.use.plugin(PLATFORM.moduleName('aurelia-animator-css'));
  // if the css animator is enabled, add swap-order="after" to all router-view elements

  // Anyone wanting to use HTMLImports to load views, will need to install the following plugin.
  // aurelia.use.plugin(PLATFORM.moduleName('aurelia-html-import-template-loader'));

  aurelia.use.developmentLogging(environment.debug ? 'debug' : 'warn');

  if (environment.testing) {
    aurelia.use.plugin(PLATFORM.moduleName('aurelia-testing'));
  }

  return aurelia.start().then(() => aurelia.setRoot(PLATFORM.moduleName('app')));
}
