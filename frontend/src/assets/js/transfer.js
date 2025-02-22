class TransferComponent {
    constructor(sourceData, targetData, sourceHeader, targetHeader) {
        this.sourceData = sourceData;
        this.targetData = targetData;
        this.sourceHeader = sourceHeader || 'Source List';
        this.targetHeader = targetHeader || 'Target List';

        this.container = document.createElement('div');
        this.container.className = 'transfer-container';

        this.sourceSearchInput = this.createSearchInput();
        this.sourceListContainer = this.createListContainer(this.sourceHeader, 'source-list', this.sourceData);

        this.targetSearchInput = this.createSearchInput();
        this.targetListContainer = this.createListContainer(this.targetHeader, 'target-list', this.targetData);

        this.buttonContainer = document.createElement('div');
        this.buttonContainer.className = 'button-container';

        const moveToTargetButton = document.createElement('button');
        moveToTargetButton.textContent = '❯';
        moveToTargetButton.onclick = () => this.moveToTarget();

        const moveToSourceButton = document.createElement('button');
        moveToSourceButton.textContent = '❮';
        moveToSourceButton.onclick = () => this.moveToSource();

        this.buttonContainer.appendChild(moveToTargetButton);
        this.buttonContainer.appendChild(moveToSourceButton);

        this.container.appendChild(this.sourceListContainer);
        this.container.appendChild(this.buttonContainer);
        this.container.appendChild(this.targetListContainer);
        

        this.sourceListContainer.appendChild(this.sourceSearchInput);        
        this.targetListContainer.appendChild(this.targetSearchInput);


    }

    createSearchInput() {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'search-input';
        input.placeholder = 'Search...';
        input.addEventListener('input', (event) => this.filterList(event));
        return input;
    }

    createListContainer(headerText, id, data) {
        const container = document.createElement('div');
        container.className = 'list-container';

        const header = document.createElement('div');
        header.className = 'list-header';
        header.textContent = headerText;

        const listBox = document.createElement('ul');
        listBox.id = id;
        listBox.className = 'list-box';

        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-item';
            listItem.textContent = item.label;
            listItem.dataset.key = item.key;
            listItem.onclick = () => this.toggleSelection(listItem);
            listBox.appendChild(listItem);
        });

        container.appendChild(header);
        container.appendChild(listBox);
        return container;
    }

    toggleSelection(item) {
        if (item.classList.contains('selected')) {
            item.classList.remove('selected');
        } else {
            item.classList.add('selected');
        }
    }

    moveToTarget() {
        const selectedItems = Array.from(document.querySelectorAll('#source-list .selected'));
        selectedItems.forEach(item => {
            const key = parseInt(item.dataset.key);
            const foundItem = this.sourceData.find(data => data.key === key);
            if (foundItem) {
                this.targetData.push(foundItem);
                this.sourceData = this.sourceData.filter(data => data.key !== key);
            }
            item.remove();
        });
        this.renderLists();
    }

    moveToSource() {
        const selectedItems = Array.from(document.querySelectorAll('#target-list .selected'));
        selectedItems.forEach(item => {
            const key = parseInt(item.dataset.key);
            const foundItem = this.targetData.find(data => data.key === key);
            if (foundItem) {
                this.sourceData.push(foundItem);
                this.targetData = this.targetData.filter(data => data.key !== key);
            }
            item.remove();
        });
        this.renderLists();
    }

    getSourceAndTarget() {
        return {
            source: this.sourceData,
            target: this.targetData
        };
    }

    reset() {
        // Move all items from target to source
        while (this.targetData.length > 0) {
            const item = this.targetData.pop();
            this.sourceData.push(item);
        }
        this.renderLists();

        return {
            source: this.sourceData,
            target: this.targetData
        }
    }

    filterList(event) {
        const inputValue = event.target.value.toLowerCase();
        const isSource = event.target === this.sourceSearchInput;
        const dataList = isSource ? this.sourceData : this.targetData;
        const listBoxId = isSource ? 'source-list' : 'target-list';
        const listBox = document.getElementById(listBoxId);

        listBox.innerHTML = '';

        dataList.forEach(item => {
            if (item.label.toLowerCase().includes(inputValue)) {
                const listItem = document.createElement('li');
                listItem.className = 'list-item';
                listItem.textContent = item.label;
                listItem.dataset.key = item.key;
                listItem.onclick = () => this.toggleSelection(listItem);
                listBox.appendChild(listItem);
            }
        });
    }

    renderLists() {
        this.filterList({ target: this.sourceSearchInput });
        this.filterList({ target: this.targetSearchInput });
    }

    mount(element) {
        element.appendChild(this.container);
    }
}

export default TransferComponent;
// Export the TransferComponent class for use in other files
// if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
//     module.exports = TransferComponent;
// } else {
//     window.TransferComponent = TransferComponent;
// }



