define([ 'base/js/namespace', 'base/js/events', 'notebook/js/notebook', 'notebook/js/codecell', 'jquery' ],
function(Jupyter, events, notebook, codecell, $) {
    function patchCodeCellExecute() {
        var proto = codecell.CodeCell.prototype;
        var orig = proto.execute;
        if (orig.isPatched) { return; }
        proto.execute = function() {
            var code = `from IPython import get_ipython
def receive_nbmeta(data):
    nbmeta = get_ipython().user_ns.setdefault('nbmeta', {})
    nbmeta['idx'] = data['idx']
    nbmeta['cells'] = data['cells']
    nbmeta['name'] = data['name']`;
            nb = Jupyter.notebook;
            nb.kernel.execute( code);
            var cellsData = nb.get_cells().map(cell => {
                var cellData = { cell_type: cell.cell_type, source: cell.get_text() };
                if (cell.cell_type === 'markdown') {cellData.attachments = cell.attachments;}
                if (cell.cell_type === 'code') {
                    cellData.outputs = cell.output_area.outputs.map(output => {
                        var outputData = { output_type: output.output_type };
                        if (output.output_type === 'stream') {
                            outputData.name = output.name;
                            outputData.text = output.text;
                        } else if (output.output_type === 'execute_result' || output.output_type === 'display_data') {
                            if (output.data['text/html']) { outputData.data = output.data['text/html']; }
                            else if (output.data['text/markdown']) { outputData.data = output.data['text/markdown']; }
                            else if (output.data['text/latex']) { outputData.data = output.data['text/latex']; }
                            else if (output.data['text/plain']) { outputData.data = output.data['text/plain']; }
                        } else if (output.output_type==='error') {
                          outputData.evalue = output.evalue;
                          outputData.tb = output.traceback.join('\n').replace(/\u001b\[\d+(?:;\d+)*m/g, '');
                        }
                        return outputData;
                    });
                }
                return cellData;
            });
            var data = { idx: nb.find_cell_index(this), name: nb.notebook_name, cells: cellsData};
            try       { var serialized = JSON.stringify(data); }
            catch (e) { console.error('Failed to serialize cell data:', e); }
            nb.kernel.execute(`receive_nbmeta(${serialized})`);
            orig.apply(this, arguments);
        };
        proto.execute.isPatched = true;
    }

    function createCell(notebook, index, ctype, text) {
        var cell;
        cell = notebook.insert_cell_below(ctype, index);
        cell.set_text(text);
        return cell;
    }

    function createCodeCell(notebook, text, index) {
        text = text.startsWith("python")? text.replace(/^python\s*\n*/, ''): `%%${text}`;
        return createCell(notebook, index, "code", text);
    }

    function splitAiReply() {
        var that = IPython.notebook;
        var index = that.get_selected_index();
        var replyCell = that.get_cell(index)
        var reply = replyCell.get_text();
        var ctype = replyCell.cell_type || 'code';
        if (ctype==='markdown'){
            var blocks = reply.split(/```/).map((block, i) => (
                {blockType: i % 2 ? "code" : "markdown", text: block.trim().replace(/^\n+|\n+$/g, '')}
            ));
            if (blocks.length === 1) return // we couldn't split the reply so we leave it as is.
            var newCellCount = 0;
            blocks.forEach(function(block, _) {
                var {blockType, text} = block;
                var newCellIndex = index+newCellCount;
                text = text.replace(/^\n+|\n+$/g, '');
                if(!text) return // in this case `return` behaves in a similar way to `continue` in a regular for loop.
                if(blockType==="code") {createCodeCell(that, text, newCellIndex); newCellCount+=1}
            });
        }
    }

    function patchSetNextInput() {
        IPython.CodeCell.prototype._handle_set_next_input = function(payload) {
            payload.cell = this;
            this.events.trigger('set_next_input.Notebook', payload);
        };
        var that = IPython.notebook;
        that.events.unbind("set_next_input.Notebook");
        that.events.on('set_next_input.Notebook', function(_, data) {
            var ctype = data.ctype || 'code';
            if (ctype==='markdown') data.execute=true;
            var index = that.find_cell_index(data.cell)+(data.offset||1);
            var cell;
            if (data.replace) that.delete_cell(index);
            cell = that.insert_cell_below(ctype, index-1);
            cell.set_text(data.text);
            if (data.execute===true) cell.execute();
            else that.dirty = true;
        });
    }

    function getCellLines(cell) {return cell.get_text().split("\n")}
    function getFirstLineParts(lines) {return (lines[0] || "").split(" ")}

    function isAiCell(cell) {
        var lines = getCellLines(cell);
        if (lines.length === 0) return false;
        var parts = getFirstLineParts(lines);
        return parts[0].startsWith("%%ai");
    }

    function isAiCellDisabled(cell){
        var lines = getCellLines(cell);
        var parts = getFirstLineParts(lines);
        return parts[1] === "0";
    }

    function disableAI(_) {
        // to disable a call to the AI we need to insert a 0 right after %%ai and before any other args.
        // for example `%%ai` => `%%ai 0` and `%%ai -m 1` => `%%ai 0 -m 1`.
        var cells = Jupyter.notebook.get_selected_cells();
        var aicells = cells.filter(cell => isAiCell(cell));
        if (aicells.length === 0) return
        // to improve usability we set all cells to the desired state of the first cell
        var disableAllCells = !isAiCellDisabled(aicells[0]);
        aicells.forEach(function(cell) {
            var lines = getCellLines(cell);
            var parts = getFirstLineParts(lines);
            // if our desired state matches our current state we do nothing.
            if (disableAllCells === isAiCellDisabled(cell)) return
            disableAllCells? parts.splice(1, 0, "0"): parts.splice(1, 1)
            lines[0] = parts.join(" ");
            cell.set_text(lines.join('\n'));
        });
    }

    function isSkippedCell(cell, skipPrefix){return cell.get_text().startsWith(skipPrefix)}

    function skipCell(_) {
        var skipPrefix = "%ai skip\n";
        var cells = Jupyter.notebook.get_selected_cells();
        var skipAllCells = !isSkippedCell(cells[0], skipPrefix);
        cells.forEach(function(cell) {
            // to skip a cell we add `%ai skip` to the top of the cell.
            var text = cell.get_text();
            // if our desired state matches our current state we do nothing.
            if (skipAllCells === isSkippedCell(cell, skipPrefix)) return
            skipAllCells? cell.set_text(skipPrefix + text): cell.set_text(text.slice(skipPrefix.length))
        });
    }

    function createAiCellMagic() {
        var notebook = Jupyter.notebook;
        var cell = notebook.get_selected_cell();
        var text = cell.get_text();
        var fullPrefix = `%%ai\n`;
        if (text.startsWith(fullPrefix)) cell.set_text(text.slice(fullPrefix.length))
        else {
            cell.set_text(fullPrefix + text)
            // to maximize ergonomics let's move the cursor to the bottom of the cell and enter edit mode,
            // so the user can start typing their prompt without any additional clicks.
            cell.code_mirror.setCursor(cell.code_mirror.lastLine(), 0);
            notebook.edit_mode();
        }
    }

    function createShortcut(name, description, cmd, defaultKeys) {
        var action = {name: name, help: description, handler: cmd};
        var full_action_name = Jupyter.actions.register(action, action.name);
        Jupyter.keyboard_manager.command_shortcuts.add_shortcut(defaultKeys, full_action_name);
    }

    function updateCellMode(cell) {
      if (cell.cell_type === 'code') {
        var firstLine = cell.get_text().split('\n')[0];
        if (firstLine.startsWith('%%ai')) cell.code_mirror.setOption('mode', 'text/plain');
      }
    }

    function load_extension() {
        patchCodeCellExecute();
        patchSetNextInput();
        createShortcut("disable ai", "disable a call to the AI for the current cell", disableAI, "Q,D");
        createShortcut("skip cell", "skip this cell when creating the AI prompt", skipCell, "Q,S");
        createShortcut("split ai reply", "split the ai reply into code cells", splitAiReply, "Q,W");
        createShortcut("create ai cell magic", "prefix a cell with %%ai", createAiCellMagic, "Q,1");
        Jupyter.notebook.events.on('kernel_ready.Kernel', _=> $('.collapse').removeClass('collapse'));
        codecell.CodeCell.options_default.highlight_modes['magic_text/x-markdown'] = {reg: [/^%%ai/]};
        Jupyter.notebook.events.on('kernel_ready.Kernel', _=> Jupyter.notebook.get_cells().forEach(updateCellMode));
        Jupyter.notebook.events.on('create.Cell', (_, data) => updateCellMode(data.cell));
        Jupyter.notebook.events.on('edit_mode.Cell', (_, data) => updateCellMode(data.cell));
    }
    return { load_ipython_extension: load_extension };
});
