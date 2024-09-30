/**
<span>${ Date.now() | dateTime & async }</span>

https://stackoverflow.com/questions/36712815/aurelia-value-converter-using-promise
 */
export class asyncBindingBehavior {

  bind(binding, source, busymessage) {
    binding.originalupdateTarget = binding.updateTarget;
    binding.updateTarget = (a) => {
      if (typeof a.then === 'function') {
        if (busymessage)
          binding.originalupdateTarget(busymessage);
        a.then(d => { binding.originalupdateTarget(d); });
      }
      else
        binding.originalupdateTarget(a);
     };
  }

  unbind(binding) {
    binding.updateTarget = binding.originalupdateTarget;
    binding.originalupdateTarget = null;
  }
}
