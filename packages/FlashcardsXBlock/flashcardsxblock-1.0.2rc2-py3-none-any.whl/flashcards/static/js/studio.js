function FlashcardsEditor(runtime, element, data) {
  (async () => {
    const {renderEditor} = await import(data.url);
    renderEditor(runtime, element[0], data);
  })();
}
