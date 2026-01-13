document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll(".admonition.dual").forEach(admonition => {
    const header = admonition.querySelector("p.admonition-title");
    const textEl = admonition.querySelector('.example-text');
    const animEl = admonition.querySelector('.example-animation');
    const infoEl = admonition.querySelector('.example-info');

    if (!header) return;
    if (!textEl) return;
    if (!animEl) return;
    if (!infoEl) return;

    // Avoid inserting multiple buttons
    if (header.querySelector(".dual-btn")) return;

    const btn = document.createElement("button");
    btn.className = "dual-btn";
    
    // Create a temporary element to measure the width of bold "Visual"
    const tempSpan = document.createElement("span");
    tempSpan.innerHTML = `<strong>${dualButtonVisual}</strong>`;
    tempSpan.style.visibility = "hidden";
    tempSpan.style.position = "absolute";
    tempSpan.style.whiteSpace = "nowrap";
    document.body.appendChild(tempSpan);
    const animatedWidth = Math.ceil(tempSpan.offsetWidth) + 5; // Add 5px padding
    document.body.removeChild(tempSpan);
    
    // Also measure "Textual" for consistency
    const tempSpan2 = document.createElement("span");
    tempSpan2.innerHTML = `<strong>${dualButtonTextual}</strong>`;
    tempSpan2.style.visibility = "hidden";
    tempSpan2.style.position = "absolute";
    tempSpan2.style.whiteSpace = "nowrap";
    document.body.appendChild(tempSpan2);
    const textualWidth = Math.ceil(tempSpan2.offsetWidth) + 5; // Add 5px padding
    document.body.removeChild(tempSpan2);
    
    btn.innerHTML = `<span class="active" style="display:inline-block;width:${textualWidth}px;text-align:right;"><strong>${dualButtonTextual}</strong></span>&nbsp;<i class="fa-solid fa-toggle-off fa-lg"></i>&nbsp;<span style="display:inline-block;width:${animatedWidth}px;text-align:left;">${dualButtonVisual}</span>`;
    infoEl.innerHTML = `<em>${dualButtonVisualText}</em>`;
    btn.onclick = function () {
      if (admonition.classList.contains("animated")) {
        admonition.classList.remove("animated");
        btn.innerHTML = `<span class="active" style="display:inline-block;width:${textualWidth}px;text-align:right;"><strong>${dualButtonTextual}</strong></span>&nbsp;<i class="fa-solid fa-toggle-off fa-lg"></i>&nbsp;<span style="display:inline-block;width:${animatedWidth}px;text-align:left;">${dualButtonVisual}</span>`;
        textEl.style.display = "block";
        animEl.style.display = "none";
        infoEl.innerHTML = `<em>${dualButtonVisualText}</em>`;
      } else {
        btn.innerHTML = `<span style="display:inline-block;width:${textualWidth}px;text-align:right;">${dualButtonTextual}</span>&nbsp;<i class="fa-solid fa-toggle-off fa-flip-horizontal fa-lg"></i>&nbsp;<span class="active" style="display:inline-block;width:${animatedWidth}px;text-align:left;"><strong>${dualButtonVisual}</strong></span>`;
        admonition.classList.add("animated");
        textEl.style.display = "none";
        animEl.style.display = "block";
        infoEl.innerHTML = `<em>${dualButtonTextualText}</em>`;
      }
    };

    // Style the button into the title bar
    header.style.position = "relative";
    btn.style.position = "absolute";
    btn.style.right = "0.5em";
    btn.style.top = "0.2em";

    header.appendChild(btn);
  });
});
