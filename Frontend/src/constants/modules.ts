export const MODULE_ICON_NAMES: Record<string, string> = {
  module_greetings: 'wave',
  module_hotel: 'building',
  module_directions: 'compass',
  module_food: 'bowl',
  module_emergency: 'shield',
  module_tour_guide: 'globe',
}

export function moduleIconName(moduleId: string) {
  return MODULE_ICON_NAMES[moduleId] ?? 'book'
}
