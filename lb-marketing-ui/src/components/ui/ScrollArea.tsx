import React from "react";

type Props = React.HTMLAttributes<HTMLDivElement> & {
  viewportClassName?: string;
};

export function ScrollArea({
  className = "",
  viewportClassName = "",
  children,
  ...props
}: Props) {
  return (
    <div className={`relative ${className}`} {...props}>
      <div className={`overflow-auto max-h-full ${viewportClassName}`}>{children}</div>
    </div>
  );
}
