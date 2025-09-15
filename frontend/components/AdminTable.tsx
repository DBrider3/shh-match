'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search } from 'lucide-react';

interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}

interface AdminTableProps {
  columns: Column[];
  data: any[];
  searchable?: boolean;
  onSearch?: (query: string) => void;
  isLoading?: boolean;
  actions?: (row: any) => React.ReactNode;
}

export function AdminTable({ 
  columns, 
  data, 
  searchable = true, 
  onSearch,
  isLoading,
  actions 
}: AdminTableProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    onSearch?.(query);
  };

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortConfig) return 0;
    
    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];
    
    if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        {searchable && (
          <div className="flex space-x-2">
            <div className="flex-1 relative">
              <div className="h-9 bg-gray-200 animate-pulse rounded"></div>
            </div>
          </div>
        )}
        <div className="border rounded-lg">
          <div className="p-4 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 animate-pulse rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {searchable && (
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="검색..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      )}

      <div className="border rounded-lg overflow-hidden">
        <table className="w-full caption-bottom text-sm">
          <thead className="[&_tr]:border-b">
            <tr className="border-b transition-colors hover:bg-muted/50">
              {columns.map((column) => (
                <th key={column.key} className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                  {column.sortable ? (
                    <Button
                      variant="ghost"
                      onClick={() => handleSort(column.key)}
                      className="h-auto p-0 font-semibold"
                    >
                      {column.label}
                      {sortConfig?.key === column.key && (
                        <span className="ml-1">
                          {sortConfig.direction === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </Button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
              {actions && <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">작업</th>}
            </tr>
          </thead>
          <tbody className="[&_tr:last-child]:border-0">
            {sortedData.length === 0 ? (
              <tr className="border-b transition-colors hover:bg-muted/50">
                <td 
                  colSpan={columns.length + (actions ? 1 : 0)} 
                  className="p-4 align-middle text-center py-8 text-gray-500"
                >
                  데이터가 없습니다.
                </td>
              </tr>
            ) : (
              sortedData.map((row, index) => (
                <tr key={row.id || index} className="border-b transition-colors hover:bg-muted/50">
                  {columns.map((column) => (
                    <td key={column.key} className="p-4 align-middle">
                      {column.render 
                        ? column.render(row[column.key], row)
                        : row[column.key]
                      }
                    </td>
                  ))}
                  {actions && (
                    <td className="p-4 align-middle">
                      {actions(row)}
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="text-sm text-gray-500">
        총 {sortedData.length}개 항목
      </div>
    </div>
  );
}