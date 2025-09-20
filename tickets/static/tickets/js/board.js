// Board functionality
document.addEventListener('DOMContentLoaded', () => {
    // Set up drag and drop handlers
    setupDragAndDrop();
    
    // Ensure we have the CSRF token
    setupCSRFToken();
});

function getCsrfToken() {
    // First try to get from input field
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    let token = csrfInput ? csrfInput.value : null;
    
    // Then try meta tag
    if (!token) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        token = metaTag ? metaTag.content : null;
    }
    
    // Finally try cookie
    if (!token) {
        const cookies = document.cookie.split('; ');
        const csrfCookie = cookies.find(row => row.startsWith('csrftoken='));
        token = csrfCookie ? csrfCookie.split('=')[1] : null;
    }
    
    if (!token) {
        throw new Error('CSRF token not found');
    }
    
    return token;
}

function setupCSRFToken() {
    try {
        // Ensure we can get a token
        const token = getCsrfToken();
        
        // If we got it from cookie but no meta tag exists, create one
        if (!document.querySelector('meta[name="csrf-token"]')) {
            const meta = document.createElement('meta');
            meta.setAttribute('name', 'csrf-token');
            meta.setAttribute('content', token);
            document.head.appendChild(meta);
        }
    } catch (error) {
        console.error('Failed to setup CSRF token:', error);
    }
}

function handleDragStart(event) {
    // Prevent dragging if the user is trying to drag a link or clicking on a link
    if (event.target.closest('a') || event.target.tagName === 'A') {
        event.preventDefault();
        return;
    }

    const ticket = event.target.closest('.ticket');
    if (!ticket) return;

    ticket.classList.add('dragging');
    event.dataTransfer.setData('text/plain', ticket.dataset.ticketId);
    event.dataTransfer.effectAllowed = 'move';
    
    // Add drag styling to columns
    document.querySelectorAll('.ticket-list').forEach(list => {
        list.classList.add('drag-active');
    });
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
    event.dataTransfer.dropEffect = 'move';

    const ticketList = event.currentTarget;
    const draggingTicket = document.querySelector('.dragging');
    
    if (!draggingTicket) return;

    // Get all tickets in this list that aren't being dragged
    const siblings = [...ticketList.querySelectorAll('.ticket:not(.dragging)')];
    
    // Find the ticket we should insert before
    const nextSibling = siblings.find(sibling => {
        const box = sibling.getBoundingClientRect();
        const offset = event.clientY - box.top - box.height / 2;
        return offset < 0;
    });

    if (nextSibling) {
        ticketList.insertBefore(draggingTicket, nextSibling);
    } else {
        ticketList.appendChild(draggingTicket);
    }
}

function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
}

function handleDragEnd(event) {
    // Remove drag styling from columns
    document.querySelectorAll('.ticket-list').forEach(list => {
        list.classList.remove('drag-active');
        list.classList.remove('drag-over');
    });
    event.target.classList.remove('dragging');
}

function calculatePosition(ticketElement, list) {
    const tickets = [...list.children];
    const position = tickets.indexOf(ticketElement) + 1;
    const totalTickets = tickets.length;
    
    // Convert position to a 1-10 scale
    return Math.round((position / totalTickets) * 9) + 1;  // Ensures range 1-10
}

function handleDrop(event) {
    event.preventDefault();
    const ticketList = event.currentTarget;
    ticketList.classList.remove('drag-over');
    
    const ticketId = event.dataTransfer.getData('text/plain');
    const ticket = document.getElementById(`ticket-${ticketId}`);
    const boardColumn = ticketList.closest('.board-column');
    const newStatus = boardColumn ? boardColumn.dataset.status : null;
    
    if (!ticket) {
        console.error('Ticket element not found:', ticketId);
        showError('Could not find ticket');
        return;
    }
    
    if (!newStatus) {
        console.error('Invalid status: ticket must be dropped in a valid column');
        showError('Invalid drop location. Please drop the ticket in a valid column.');
        return;
    }

    // Check if the ticket is already in this list
    if (ticket.parentElement === ticketList) {
        // Just update the position if the ticket was reordered in the same list
        const position = calculatePosition(ticket, ticketList);
        updateTicket(ticketId, newStatus, position).catch(error => {
            console.error('Failed to update ticket position:', error);
            showError('Failed to update ticket position');
        });
        return;
    }
    
    // Store the original parent and position for rollback
    const originalParent = ticket.parentElement;
    const originalNextSibling = ticket.nextSibling;
    
    // Move the ticket to the new list first for better UX
    ticketList.appendChild(ticket);
    ticket.classList.remove('dragging');
    
    // Get position in the new list
    const position = calculatePosition(ticket, ticketList);
    
    // Update the ticket in the backend
    updateTicket(ticketId, newStatus, position).catch(error => {
        console.error('Failed to update ticket:', error);
        showError('Failed to update ticket. Rolling back changes...');
        
        // Rollback the DOM changes
        if (originalNextSibling) {
            originalParent.insertBefore(ticket, originalNextSibling);
        } else {
            originalParent.appendChild(ticket);
        }
    });
}

async function updateTicket(ticketId, newStatus, position) {
    let retryCount = 0;
    const maxRetries = 3;
    const baseDelay = 1000; // Start with 1 second delay

    while (retryCount < maxRetries) {
        try {
            // First update the status
            const statusResponse = await fetch('/update-ticket-status/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    ticket_id: ticketId,
                    new_status: newStatus
                })
            });

            if (!statusResponse.ok) {
                if (statusResponse.status === 403) {
                    throw new Error('Permission denied. You may not have the right access level.');
                }
                if (statusResponse.status === 401) {
                    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }
                throw new Error(`Status update failed: ${statusResponse.statusText}`);
            }

            const statusData = await statusResponse.json();
            if (!statusData.success) {
                throw new Error(statusData.error || 'Status update failed');
            }
            
            // Then update the position
            const positionResponse = await fetch('/api/tickets/update-position/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    ticket_id: ticketId,
                    importance: Math.min(Math.max(position, 1), 10), // Ensure between 1-10
                    urgency: 5 // Default to medium urgency
                })
            });

            if (!positionResponse.ok) {
                if (positionResponse.status === 403) {
                    throw new Error('Permission denied. You may not have the right access level.');
                }
                if (positionResponse.status === 401) {
                    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }
                throw new Error(`Position update failed: ${positionResponse.statusText}`);
            }

            const positionData = await positionResponse.json();
            if (!positionData.success) {
                throw new Error(positionData.error || 'Position update failed');
            }

            showSuccess('Ticket updated successfully');
            return true;
            
        } catch (error) {
            console.error(`Error updating ticket (attempt ${retryCount + 1}/${maxRetries}):`, error);
            
            // Network errors or server timeouts might be temporary
            if (error instanceof TypeError || error.message.includes('timeout') || error.message.includes('network')) {
                retryCount++;
                if (retryCount < maxRetries) {
                    const delay = baseDelay * Math.pow(2, retryCount); // Exponential backoff
                    showMessage(`Retrying update in ${delay/1000} seconds...`, 'info');
                    await new Promise(resolve => setTimeout(resolve, delay));
                    continue;
                }
            }
            
            showError(error.message);
            throw error;
        }
    }
    
    throw new Error('Failed to update ticket after multiple retries');
}

function showSuccess(message) {
    showMessage(message, 'success');
}

function showError(message) {
    showMessage(message, 'error');
}

function showMessage(message, type = 'info') {
    const container = document.querySelector('.message-container') || createMessageContainer();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    container.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
        if (container.children.length === 0) {
            container.remove();
        }
    }, 3000);
}

function createMessageContainer() {
    const container = document.createElement('div');
    container.className = 'message-container';
    document.body.appendChild(container);
    return container;
}

function setupDragAndDrop() {
    function initializeTicket(ticket) {
        if (!ticket.hasAttribute('data-drag-initialized')) {
            ticket.setAttribute('draggable', true);
            ticket.setAttribute('data-drag-initialized', 'true');
            ticket.addEventListener('dragstart', handleDragStart);
            ticket.addEventListener('dragend', handleDragEnd);
        }
    }

    function initializeList(list) {
        if (!list.hasAttribute('data-drop-initialized')) {
            list.setAttribute('data-drop-initialized', 'true');
            list.addEventListener('dragover', handleDragOver);
            list.addEventListener('dragleave', handleDragLeave);
            list.addEventListener('drop', handleDrop);
        }
    }

    // Initialize existing elements
    document.querySelectorAll('.ticket').forEach(initializeTicket);
    document.querySelectorAll('.ticket-list').forEach(initializeList);

    // Setup observer for dynamic content
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // Check if the added node is a ticket or contains tickets
                    if (node.classList.contains('ticket')) {
                        initializeTicket(node);
                    }
                    node.querySelectorAll('.ticket').forEach(initializeTicket);

                    // Check if the added node is a list or contains lists
                    if (node.classList.contains('ticket-list')) {
                        initializeList(node);
                    }
                    node.querySelectorAll('.ticket-list').forEach(initializeList);
                }
            });
        });
    });

    // Observe the entire board for changes
    const board = document.querySelector('.board');
    if (board) {
        observer.observe(board, {
            childList: true,
            subtree: true
        });
    }
}