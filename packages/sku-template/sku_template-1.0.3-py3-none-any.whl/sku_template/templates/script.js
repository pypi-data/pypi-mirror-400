// HTML报告生成器JavaScript代码

// 抑制浏览器扩展相关的错误
(function() {
    try {
        // 静默处理扩展连接错误
        const originalError = console.error;
        console.error = function(...args) {
            if (args.length > 0 && typeof args[0] === 'string' && 
                (args[0].includes('Could not establish connection') || 
                 args[0].includes('Receiving end does not exist') ||
                 args[0].includes('runtime.lastError'))) {
                return; // 忽略扩展连接错误
            }
            originalError.apply(console, args);
        };
    } catch (e) {
        // 忽略错误处理本身的错误
    }
})();

// 多层嵌套展示的切换函数
function toggleDetails(id) {
    const details = document.getElementById(id);
    if (details.style.display === 'none' || details.style.display === '') {
        details.style.display = 'block';
        // 保存详细信息打开状态
        const detailsKey = window.location.pathname + '_details_' + id;
        localStorage.setItem(detailsKey, 'true');
    } else {
        details.style.display = 'none';
        // 保存详细信息关闭状态
        const detailsKey = window.location.pathname + '_details_' + id;
        localStorage.setItem(detailsKey, 'false');
    }
}

// 更新汇总信息
function updateSummary() {
    // 获取所有状态选择框
    const selects = document.querySelectorAll('select.status-select[id^="status_"]');
    
    let totalCases = 0;
    let passedCases = 0;
    let failedCases = 0;
    
    selects.forEach(function(select) {
        totalCases++;
        const value = select.value;
        if (value === 'pass') {
            passedCases++;
        } else {
            // diff 和 fail 都算作失败
            failedCases++;
        }
    });
    
    // 计算通过率
    const passRate = totalCases > 0 ? (passedCases / totalCases * 100).toFixed(1) : '0.0';
    
    // 更新DOM元素
    const totalElement = document.getElementById('summary-total-cases');
    const passedElement = document.getElementById('summary-passed-cases');
    const failedElement = document.getElementById('summary-failed-cases');
    const passRateElement = document.getElementById('summary-pass-rate');
    
    if (totalElement) totalElement.textContent = totalCases;
    if (passedElement) passedElement.textContent = passedCases;
    if (failedElement) failedElement.textContent = failedCases;
    if (passRateElement) passRateElement.textContent = passRate + '%';
}

// 更新状态选择框的样式
function updateStatus(index, value) {
    const select = document.getElementById('status_' + index);
    
    if (!select) {
        console.error('未找到状态选择框: status_' + index);
        return;
    }
    
    // 移除所有状态类
    select.classList.remove('status-pass', 'status-diff', 'status-fail');
    
    // 根据选择的值添加对应的状态类
    if (value === 'pass') {
        select.classList.add('status-pass');
    } else if (value === 'diff') {
        select.classList.add('status-diff');
    } else if (value === 'fail') {
        select.classList.add('status-fail');
    }
    
    // 保存状态到localStorage（使用页面URL作为key的一部分，避免不同报告冲突）
    const pageKey = window.location.pathname + '_status_' + index;
    localStorage.setItem(pageKey, value);
    
    // 更新行的data-status属性（用于过滤）
    const row = select.closest('tr');
    if (row) {
        row.setAttribute('data-status', value);
        // 如果当前有过滤条件，检查是否需要隐藏/显示这行
        const currentFilter = localStorage.getItem(window.location.pathname + '_current_filter') || 'all';
        if (currentFilter !== 'all') {
            if (value !== currentFilter) {
                row.classList.add('filter-hidden');
            } else {
                row.classList.remove('filter-hidden');
            }
            updateFilterCount();
        }
    }
    
    // 更新汇总信息
    updateSummary();
    
    // 可选：显示提示信息
    console.log('用例 ' + index + ' 状态已更新为: ' + value + ' (已保存)');
}

// 切换到编辑模式
function editNote(index, event) {
    // 阻止事件冒泡，避免触发其他点击事件
    if (event) {
        event.stopPropagation();
    }
    
    const displayDiv = document.getElementById('note_display_' + index);
    const textarea = document.getElementById('note_' + index);
    const noteText = document.getElementById('note_text_' + index);
    
    if (!displayDiv || !textarea || !noteText) {
        console.error('未找到备注元素: note_' + index);
        return;
    }
    
    // 隐藏显示文本，显示输入框
    displayDiv.style.display = 'none';
    textarea.style.display = 'block';
    
    // 设置输入框的值
    const currentText = noteText.textContent.trim();
    if (currentText) {
        textarea.value = currentText;
    } else {
        textarea.value = '';
    }
    
    // 聚焦输入框
    setTimeout(function() {
        textarea.focus();
        // 将光标移到末尾
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    }, 10);
}

// 保存备注并切换回显示模式
function saveNote(index, event) {
    // 使用延迟执行，避免在点击其他元素时立即触发导致错误
    setTimeout(function() {
        try {
            const displayDiv = document.getElementById('note_display_' + index);
            const textarea = document.getElementById('note_' + index);
            const noteText = document.getElementById('note_text_' + index);
            
            // 检查元素是否存在
            if (!displayDiv || !textarea || !noteText) {
                return; // 静默返回，不输出错误
            }
            
            // 如果输入框已经隐藏，说明已经处理过了，直接返回
            if (textarea.style.display === 'none' || textarea.offsetParent === null) {
                return;
            }
            
            // 检查当前聚焦的元素，如果是备注相关的元素，不保存（避免在切换编辑模式时触发）
            const activeElement = document.activeElement;
            if (activeElement && (
                activeElement.id === 'note_display_' + index ||
                activeElement.id === 'note_' + index ||
                activeElement.id === 'note_text_' + index ||
                (activeElement.closest && activeElement.closest('.status-note-wrapper'))
            )) {
                return; // 如果聚焦的是备注相关元素，不保存
            }
            
            const value = textarea.value.trim();
            
            // 更新显示文本
            if (value) {
                noteText.textContent = value;
                noteText.classList.remove('empty-note');
            } else {
                noteText.textContent = '';
                noteText.classList.add('empty-note');
            }
            
            // 保存到localStorage
            updateNote(index, value);
            
            // 切换回显示模式
            displayDiv.style.display = 'block';
            textarea.style.display = 'none';
        } catch (e) {
            // 静默处理任何错误，避免影响其他功能
            console.debug('保存备注时出现错误（已忽略）:', e);
        }
    }, 150); // 延迟150ms，确保点击事件完成
}

// 更新备注（内部函数，用于保存到localStorage）
function updateNote(index, value) {
    // 保存备注到localStorage（使用页面URL作为key的一部分，避免不同报告冲突）
    const pageKey = window.location.pathname + '_note_' + index;
    localStorage.setItem(pageKey, value);
    
    // 可选：显示提示信息
    if (value) {
        console.log('用例 ' + index + ' 备注已更新: ' + value.substring(0, 20) + (value.length > 20 ? '...' : '') + ' (已保存)');
    }
}

// 页面加载时恢复所有状态
function restoreAllStatuses() {
    const pagePath = window.location.pathname;
    const selects = document.querySelectorAll('select.status-select[id^="status_"]');
    
    selects.forEach(function(select) {
        const id = select.id;
        // 提取索引
        const match = id.match(/status_(\d+)/);
        if (match) {
            const index = match[1];
            const pageKey = pagePath + '_status_' + index;
            const savedValue = localStorage.getItem(pageKey);
            
            // 如果localStorage中有保存的值，优先使用它（覆盖HTML中的默认值）
            // 如果没有保存的值，使用HTML中的初始值（可能是外部设置的）
            const currentValue = select.value;
            const valueToUse = savedValue && (savedValue === 'pass' || savedValue === 'diff' || savedValue === 'fail') 
                ? savedValue 
                : currentValue;
            
            // 如果localStorage中有保存的值，使用它；否则使用HTML中的初始值
            if (savedValue && (savedValue === 'pass' || savedValue === 'diff' || savedValue === 'fail')) {
                // 恢复选择的值
                select.value = savedValue;
                // 更新HTML中的selected属性
                const options = select.querySelectorAll('option');
                options.forEach(function(option) {
                    option.removeAttribute('selected');
                    if (option.value === savedValue) {
                        option.setAttribute('selected', 'selected');
                    }
                });
                // 更新样式（但不触发保存，避免循环）
                select.classList.remove('status-pass', 'status-diff', 'status-fail');
                select.classList.add('status-' + savedValue);
                
                // 更新行的data-status属性
                const row = select.closest('tr');
                if (row) {
                    row.setAttribute('data-status', savedValue);
                }
            } else {
                // 如果没有保存的值，确保HTML中的初始值（可能是外部设置的）被保存到localStorage
                if (currentValue && (currentValue === 'pass' || currentValue === 'diff' || currentValue === 'fail')) {
                    localStorage.setItem(pageKey, currentValue);
                }
            }
        }
    });
    
    // 恢复所有备注
    restoreAllNotes();
}

// 页面加载时恢复所有备注
function restoreAllNotes() {
    const pagePath = window.location.pathname;
    const noteTexts = document.querySelectorAll('span.note-text[id^="note_text_"]');
    
    noteTexts.forEach(function(noteText) {
        const id = noteText.id;
        // 提取索引
        const match = id.match(/note_text_(\d+)/);
        if (match) {
            const index = match[1];
            const pageKey = pagePath + '_note_' + index;
            
            // 优先使用localStorage中保存的备注（用户手动修改的）
            let noteContent = localStorage.getItem(pageKey);
            
            // 如果localStorage中没有，则使用外部设置的初始备注
            if (!noteContent || !noteContent.trim()) {
                const initialNote = noteText.getAttribute('data-initial-note');
                if (initialNote && initialNote.trim()) {
                    noteContent = initialNote;
                    // 将外部设置的备注也保存到localStorage，以便后续使用
                    localStorage.setItem(pageKey, noteContent);
                }
            }
            
            // 显示备注内容
            if (noteContent && noteContent.trim()) {
                noteText.textContent = noteContent;
                noteText.classList.remove('empty-note');
                
                // 同时更新对应的 textarea（虽然隐藏，但导出时需要）
                const textarea = document.getElementById('note_' + index);
                if (textarea) {
                    textarea.value = noteContent;
                }
            } else {
                // 没有备注时清空，让CSS的:empty伪类显示占位符
                noteText.textContent = '';
                noteText.classList.add('empty-note');
            }
        }
    });
}

// 状态过滤功能
let currentFilter = 'all';

function filterByStatus(status) {
    currentFilter = status;
    // 保存当前过滤条件到localStorage
    localStorage.setItem(window.location.pathname + '_current_filter', status);
    
    // 获取所有表格行（只选择直接子级tr，避免选择到详细信息里的表格行）
    const tbody = document.getElementById('test-cases-table-body');
    if (!tbody) return;
    
    // 只选择直接子级tr，避免选择到详细信息里的嵌套表格的tr
    const rows = Array.from(tbody.children).filter(function(child) {
        return child.tagName === 'TR' && child.hasAttribute('data-status');
    });
    
    let visibleCount = 0;
    
    rows.forEach(function(row) {
        const rowStatus = row.getAttribute('data-status');
        const rowIndex = row.getAttribute('data-row-index');
        
        if (status === 'all' || rowStatus === status) {
            // 显示行：移除filter-hidden类，而不是直接设置display
            row.classList.remove('filter-hidden');
            visibleCount++;
        } else {
            // 隐藏行：添加filter-hidden类，而不是直接设置display
            row.classList.add('filter-hidden');
        }
    });
    
    // 使用setTimeout确保在DOM更新后恢复详细信息状态
    setTimeout(function() {
        rows.forEach(function(row) {
            if (!row.classList.contains('filter-hidden')) {
                const rowIndex = row.getAttribute('data-row-index');
                if (rowIndex) {
                    const detailsId = 'details_' + rowIndex;
                    const detailsDiv = document.getElementById(detailsId);
                    if (detailsDiv) {
                        // 从localStorage恢复详细信息状态
                        const detailsKey = window.location.pathname + '_details_' + detailsId;
                        const wasOpen = localStorage.getItem(detailsKey) === 'true';
                        if (wasOpen) {
                            detailsDiv.style.display = 'block';
                        }
                    }
                }
            }
        });
    }, 0);
    
    // 更新过滤器按钮状态
    updateFilterButtons(status);
    
    // 更新显示数量
    updateFilterCount();
}

function updateFilterButtons(activeStatus) {
    // 移除所有按钮的active类
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(function(btn) {
        btn.classList.remove('active');
        // 重置按钮样式
        const status = btn.id.replace('filter-', '');
        if (status === 'all') {
            btn.style.background = 'white';
            btn.style.color = '#7c8fc2';
            btn.style.borderColor = '#7c8fc2';
        } else if (status === 'pass') {
            btn.style.background = 'white';
            btn.style.color = '#5db884';
            btn.style.borderColor = '#5db884';
        } else if (status === 'diff') {
            btn.style.background = 'white';
            btn.style.color = '#d6a884';
            btn.style.borderColor = '#d6a884';
        } else if (status === 'fail') {
            btn.style.background = 'white';
            btn.style.color = '#d6848a';
            btn.style.borderColor = '#d6848a';
        }
    });
    
    // 激活当前按钮
    const activeButton = document.getElementById('filter-' + activeStatus);
    if (activeButton) {
        activeButton.classList.add('active');
        if (activeStatus === 'all') {
            activeButton.style.background = '#7c8fc2';
            activeButton.style.color = 'white';
        } else if (activeStatus === 'pass') {
            activeButton.style.background = '#5db884';
            activeButton.style.color = 'white';
        } else if (activeStatus === 'diff') {
            activeButton.style.background = '#d6a884';
            activeButton.style.color = 'white';
        } else if (activeStatus === 'fail') {
            activeButton.style.background = '#d6848a';
            activeButton.style.color = 'white';
        }
    }
}

function updateFilterCount() {
    // 只选择直接子级tr，避免选择到详细信息里的嵌套表格的tr
    const tbody = document.getElementById('test-cases-table-body');
    if (!tbody) return;
    
    const rows = Array.from(tbody.children).filter(function(child) {
        return child.tagName === 'TR' && child.hasAttribute('data-status');
    });
    
    const visibleRows = rows.filter(function(row) {
        return !row.classList.contains('filter-hidden');
    });
    const totalRows = rows.length;
    const visibleCount = visibleRows.length;
    
    const countElement = document.getElementById('filter-count');
    if (countElement) {
        if (currentFilter === 'all') {
            countElement.textContent = `显示全部 ${totalRows} 个用例`;
        } else {
            countElement.textContent = `显示 ${visibleCount} / ${totalRows} 个用例`;
        }
    }
}

// 恢复详细信息的状态
function restoreDetailsStates() {
    const pagePath = window.location.pathname;
    const allDetails = document.querySelectorAll('.details');
    
    allDetails.forEach(function(details) {
        const detailsId = details.id;
        if (detailsId) {
            const detailsKey = pagePath + '_details_' + detailsId;
            const wasOpen = localStorage.getItem(detailsKey) === 'true';
            if (wasOpen) {
                details.style.display = 'block';
            }
        }
    });
}

// 页面加载完成后恢复状态
document.addEventListener('DOMContentLoaded', function() {
    restoreAllStatuses();
    // 恢复状态后更新汇总信息
    updateSummary();
    
    // 恢复详细信息状态
    restoreDetailsStates();
    
    // 恢复过滤状态
    const savedFilter = localStorage.getItem(window.location.pathname + '_current_filter') || 'all';
    filterByStatus(savedFilter);
    
    // 备注已经在 restoreAllStatuses 中通过 restoreAllNotes 恢复了
});

// 导出修改后的HTML文件（将当前状态保存到HTML中）
function exportModifiedHTML() {
    // 获取所有状态选择框并更新HTML中的selected属性
    const selects = document.querySelectorAll('select.status-select[id^="status_"]');
    
    selects.forEach(function(select) {
        const id = select.id;
        const match = id.match(/status_(\d+)/);
        if (match) {
            const index = match[1];
            const currentValue = select.value;
            
            // 更新HTML中对应的option的selected属性
            const options = select.querySelectorAll('option');
            options.forEach(function(option) {
                option.removeAttribute('selected');
                if (option.value === currentValue) {
                    option.setAttribute('selected', 'selected');
                }
            });
            
            // 更新class属性
            select.className = 'status-select status-' + currentValue;
        }
    });
    
    // 获取所有备注输入框并更新HTML中的显示文本
    // 需要同时处理显示状态和编辑状态的备注
    const noteTexts = document.querySelectorAll('span.note-text[id^="note_text_"]');
    
    noteTexts.forEach(function(noteText) {
        const id = noteText.id;
        const match = id.match(/note_text_(\d+)/);
        if (match) {
            const index = match[1];
            
            // 优先获取 textarea 的值（可能正在编辑中）
            const textarea = document.getElementById('note_' + index);
            let currentNote = '';
            
            if (textarea) {
                // 如果 textarea 有值，使用 textarea 的值（可能是用户正在编辑但未保存的）
                currentNote = textarea.value || '';
            }
            
            // 如果 textarea 没有值，使用 noteText 的当前内容
            if (!currentNote || !currentNote.trim()) {
                currentNote = noteText.textContent || '';
            }
            
            // 同步更新显示文本，确保导出的HTML中显示最新的备注
            if (currentNote && currentNote.trim()) {
                noteText.textContent = currentNote;
                noteText.classList.remove('empty-note');
                // 同时更新 textarea 的值，确保一致性
                if (textarea) {
                    textarea.value = currentNote;
                }
            } else {
                noteText.textContent = '';
                noteText.classList.add('empty-note');
                // 同时清空 textarea
                if (textarea) {
                    textarea.value = '';
                }
            }
        }
    });
    
    // 获取完整的HTML内容
    const htmlContent = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
    
    // 创建下载链接
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // 生成文件名（基于当前时间戳）
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const originalFileName = window.location.pathname.split('/').pop() || 'report.html';
    const fileName = originalFileName.replace('.html', '_modified_' + timestamp + '.html');
    
    link.download = fileName;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    alert('✅ 修改后的HTML文件已导出（包含状态和备注）：' + fileName);
}

