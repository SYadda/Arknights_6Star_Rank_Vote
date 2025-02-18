class TableComponent {
    constructor(data, labels) {
        this.data = data;
        this.labels = labels;

        this.container = document.createElement('div');
        this.container.className = 'table-container';

        this.headerRow = this.createHeaderRow();
        this.bodyRows = this.createBodyRows();

        this.container.appendChild(this.headerRow);
        this.bodyRows.forEach(row => this.container.appendChild(row));
    }

    createHeaderRow() {
        const headerRow = document.createElement('div');
        headerRow.className = 'table-header table-row';

        // Add an empty cell for the row label column
        const emptyCell = document.createElement('div');
        emptyCell.className = 'table-cell row-label';
        headerRow.appendChild(emptyCell);

        this.labels.forEach(label => {
            const cell = document.createElement('div');
            cell.className = 'table-cell';
            cell.textContent = label;

            headerRow.appendChild(cell);
        });

        return headerRow;
    }

    createBodyRows() {
        return this.data.map((rowData, rowIndex) => {
            const row = document.createElement('div');
            row.className = 'table-row';
            row.onclick = () => this.selectRow(row);

            // Add row label cell
            const rowLabelCell = document.createElement('div');
            rowLabelCell.className = 'table-cell row-label';
            rowLabelCell.textContent = this.labels[rowIndex];
            row.appendChild(rowLabelCell);

            rowData.forEach(value => {
                const cell = document.createElement('div');
                cell.className = 'table-cell';
                cell.textContent = value;

                row.appendChild(cell);
            });

            return row;
        });
    }

    selectRow(row) {
        const selectedRows = this.container.querySelectorAll('.selected');
        selectedRows.forEach(selectedRow => selectedRow.classList.remove('selected'));

        row.classList.add('selected');
    }

    updateData(newData, newLabels) {
        this.data = newData;
        this.labels = newLabels;

        // Clear existing content
        this.container.innerHTML = '';

        // Recreate header and body rows
        this.headerRow = this.createHeaderRow();
        this.bodyRows = this.createBodyRows();

        // Append new header and body rows to the container
        this.container.appendChild(this.headerRow);
        this.bodyRows.forEach(row => this.container.appendChild(row));
    }

    mount(element) {
        element.appendChild(this.container);
    }
}

// Export the TableComponent class for use in other files
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = TableComponent;
} else {
    window.TableComponent = TableComponent;
}



