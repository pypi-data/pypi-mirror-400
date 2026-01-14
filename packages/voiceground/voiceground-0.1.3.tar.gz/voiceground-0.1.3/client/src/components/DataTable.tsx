import { ReactNode } from 'react';
import {
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Column<T> {
  header: ReactNode;
  cell: (row: T, index: number) => ReactNode;
  className?: string;
  cellClassName?: string | ((row: T, index: number) => string);
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
  className?: string;
  onRowMouseEnter?: (row: T, index: number) => void;
  onRowMouseLeave?: (row: T, index: number) => void;
  rowClassName?: (row: T, index: number) => string;
  getRowKey?: (row: T, index: number) => string | number;
}

export function DataTable<T>({ 
  columns, 
  data, 
  emptyMessage = 'No data available',
  className,
  onRowMouseEnter,
  onRowMouseLeave,
  rowClassName,
  getRowKey,
}: DataTableProps<T>) {
  return (
    <div className={`h-full flex flex-col min-h-0 overflow-hidden ${className || ''}`}>
      <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
        <ScrollArea className="flex-1 min-h-0">
          <table className="w-full caption-bottom text-sm" style={{ tableLayout: 'fixed' }}>
            <TableHeader className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
              <TableRow className="hover:bg-transparent">
                {columns.map((column, index) => (
                  <TableHead key={index} className={column.className}>
                    {column.header}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={columns.length} className="text-center text-muted-foreground py-8">
                    {emptyMessage}
                  </TableCell>
                </TableRow>
              ) : (
                data.map((row, rowIndex) => (
                  <TableRow 
                    key={getRowKey ? getRowKey(row, rowIndex) : rowIndex}
                    className={rowClassName ? rowClassName(row, rowIndex) : ''}
                    onMouseEnter={() => onRowMouseEnter?.(row, rowIndex)}
                    onMouseLeave={() => onRowMouseLeave?.(row, rowIndex)}
                  >
                    {columns.map((column, colIndex) => {
                      const cellClassName = typeof column.cellClassName === 'function'
                        ? column.cellClassName(row, rowIndex)
                        : column.cellClassName;
                      return (
                        <TableCell 
                          key={colIndex} 
                          className={`${column.className || ''} ${cellClassName || ''}`.trim()}
                        >
                          {column.cell(row, rowIndex)}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))
              )}
            </TableBody>
          </table>
        </ScrollArea>
      </div>
    </div>
  );
}

