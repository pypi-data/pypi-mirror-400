import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface DataTableColumnHeaderProps {
  title: string
  sortAsc?: boolean | null
  onSortChange?: (asc: boolean) => void
  filterOptions?: Array<{ value: string; label: string }>
  filterValue?: string
  onFilterChange?: (value: string) => void
  className?: string
}

export function DataTableColumnHeader({
  title,
  sortAsc,
  onSortChange,
  filterOptions,
  filterValue,
  onFilterChange,
  className,
}: DataTableColumnHeaderProps) {
  const canSort = onSortChange !== undefined
  const canFilter = filterOptions !== undefined && onFilterChange !== undefined

  if (!canSort && !canFilter) {
    return <div className={cn(className)}>{title}</div>
  }

  return (
    <div className={cn("flex items-center gap-2", className)}>
      {canFilter ? (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="data-[state=open]:bg-accent -ml-3 h-8"
            >
              <span>{title}</span>
              {canSort && (
                <>
                  {sortAsc === true ? (
                    <ArrowUp className="ml-2 h-4 w-4" />
                  ) : sortAsc === false ? (
                    <ArrowDown className="ml-2 h-4 w-4" />
                  ) : (
                    <ChevronsUpDown className="ml-2 h-4 w-4" />
                  )}
                </>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            {canSort && (
              <>
                <DropdownMenuItem onClick={() => onSortChange?.(true)}>
                  <ArrowUp className="mr-2 h-4 w-4" />
                  Asc
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onSortChange?.(false)}>
                  <ArrowDown className="mr-2 h-4 w-4" />
                  Desc
                </DropdownMenuItem>
                {filterOptions && filterOptions.length > 0 && (
                  <DropdownMenuSeparator />
                )}
              </>
            )}
            {filterOptions?.map((option) => (
              <DropdownMenuItem
                key={option.value}
                onClick={() => onFilterChange?.(option.value)}
                className={cn(
                  filterValue === option.value && "bg-accent"
                )}
              >
                {option.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      ) : (
        <Button
          variant="ghost"
          size="sm"
          className="data-[state=open]:bg-accent -ml-3 h-8"
          onClick={() => {
            if (sortAsc === null || sortAsc === false) {
              onSortChange?.(true)
            } else {
              onSortChange?.(false)
            }
          }}
        >
          <span>{title}</span>
          {sortAsc === true ? (
            <ArrowUp className="ml-2 h-4 w-4" />
          ) : sortAsc === false ? (
            <ArrowDown className="ml-2 h-4 w-4" />
          ) : (
            <ChevronsUpDown className="ml-2 h-4 w-4" />
          )}
        </Button>
      )}
    </div>
  )
}

