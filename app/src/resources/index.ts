import {FrameworkConfiguration} from 'aurelia-framework';
import {PLATFORM} from 'aurelia-pal';

export function configure(config: FrameworkConfiguration) {
    config.globalResources([
        PLATFORM.moduleName('resources/async'),
        PLATFORM.moduleName('resources/keys'),
        PLATFORM.moduleName('resources/number-format'),
    ]);
}
