'use client';
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ChevronRight } from 'lucide-react';

export interface Column<T> {
  header: string;
  accessorKey?: keyof T;
  cell?: (row: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  renderExpandedRow?: (row: T) => React.ReactNode;
  keyExtractor: (row: T) => string;
}

export function DataTable<T>({ data, columns, renderExpandedRow, keyExtractor }: DataTableProps<T>) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [sortConfig, setSortConfig] = useState<{ key: keyof T; direction: 'asc' | 'desc' } | null>(null);

  const toggleRow = (key: string) => {
    const next = new Set(expandedRows);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    setExpandedRows(next);
  };

  const handleSort = (key: keyof T) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedData = React.useMemo(() => {
    if (!sortConfig) return data;
    return [...data].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortConfig]);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-slate-900 border-b border-slate-800">
            {renderExpandedRow && <th className="p-4 w-10"></th>}
            {columns.map((col, idx) => (
              <th 
                key={idx} 
                className={`p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider ${col.sortable ? 'cursor-pointer select-none hover:text-slate-300' : ''}`}
                onClick={() => col.sortable && col.accessorKey && handleSort(col.accessorKey)}
              >
                <div className="flex items-center gap-1">
                  {col.header}
                  {col.sortable && sortConfig !== null && sortConfig.key === col.accessorKey && (
                    sortConfig.direction === 'asc' ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900">
          {sortedData.map((row) => {
            const key = keyExtractor(row);
            const isExpanded = expandedRows.has(key);
            return (
              <React.Fragment key={key}>
                <tr 
                  className={`table-row-hover ${isExpanded ? 'bg-slate-800/50' : ''}`} 
                  onClick={() => renderExpandedRow && toggleRow(key)}
                >
                  {renderExpandedRow && (
                    <td className="p-4 text-slate-500">
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </td>
                  )}
                  {columns.map((col, idx) => (
                    <td key={idx} className="p-4 text-sm text-slate-300">
                      {col.cell ? col.cell(row) : col.accessorKey ? String(row[col.accessorKey]) : null}
                    </td>
                  ))}
                </tr>
                {isExpanded && renderExpandedRow && (
                  <tr className="bg-slate-950 border-t border-slate-800">
                    <td colSpan={columns.length + 1} className="p-0">
                      {renderExpandedRow(row)}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
