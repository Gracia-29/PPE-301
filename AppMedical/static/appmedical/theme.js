document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("[data-sidebar]");
  const toggle = document.querySelector("[data-sidebar-toggle]");

  if (sidebar && toggle) {
    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("is-open");
    });
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  document.querySelectorAll("[data-reveal]").forEach((node) => observer.observe(node));

  document.querySelectorAll("[data-field-group]").forEach((group) => {
    const input = group.querySelector("[data-form-input]");
    const help = group.querySelector("[data-field-help]");

    if (!input || !help || group.classList.contains("has-errors")) {
      return;
    }

    const updateHelpVisibility = () => {
      const hasValue = input.value.trim() !== "";
      const isFocused = document.activeElement === input;
      group.classList.toggle("is-help-visible", isFocused || hasValue);
      help.hidden = !(isFocused || hasValue);
    };

    input.addEventListener("focus", updateHelpVisibility);
    input.addEventListener("blur", updateHelpVisibility);
    input.addEventListener("input", updateHelpVisibility);
    input.addEventListener("change", updateHelpVisibility);

    updateHelpVisibility();
  });

  document.querySelectorAll("[data-form-wizard]").forEach((wizard) => {
    const steps = Array.from(wizard.querySelectorAll("[data-form-step]"));
    const indicators = Array.from(document.querySelectorAll("[data-step-indicator]"));
    const startStep = Number(wizard.dataset.startStep || 1);
    let currentStep = startStep;

    const renderStep = () => {
      steps.forEach((step) => {
        step.classList.toggle("is-active", Number(step.dataset.formStep) === currentStep);
      });

      indicators.forEach((indicator) => {
        indicator.classList.toggle("is-active", Number(indicator.dataset.stepIndicator) === currentStep);
      });
    };

    const validateStep = (stepNumber) => {
      const currentPanel = wizard.querySelector(`[data-form-step="${stepNumber}"]`);
      if (!currentPanel) {
        return true;
      }

      const fields = currentPanel.querySelectorAll("input, select, textarea");
      for (const field of fields) {
        if (!field.checkValidity()) {
          field.reportValidity();
          return false;
        }
      }
      return true;
    };

    wizard.querySelectorAll("[data-step-next]").forEach((button) => {
      button.addEventListener("click", () => {
        if (!validateStep(currentStep)) {
          return;
        }
        currentStep = Math.min(currentStep + 1, steps.length);
        renderStep();
      });
    });

    wizard.querySelectorAll("[data-step-prev]").forEach((button) => {
      button.addEventListener("click", () => {
        currentStep = Math.max(currentStep - 1, 1);
        renderStep();
      });
    });

    if (wizard.querySelector(".field-error")) {
      const hasStepTwoErrors = wizard.querySelector('[data-form-step="2"] .field-error');
      currentStep = hasStepTwoErrors ? 2 : 1;
    }

    renderStep();
  });
});
