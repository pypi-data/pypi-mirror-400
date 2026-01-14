#pragma once

#include <algorithm>
#include <utility>
#include <vector>

#include <urx/group.h>

#include <uac/event.h>
#include <uac/igroup.h>

namespace uac {

struct Group : urx::detail::Group<Event>, IGroup {
  bool operator==(const IGroup& other) const override {
    const Group* pointer = dynamic_cast<const Group*>(&other);
    return pointer != nullptr && urx::detail::Group<Event>::operator==(*pointer) &&
           IGroup::operator==(other);
  }

  bool operator!=(const IGroup& other) const override { return !operator==(other); }

  bool secureComparison(
      const IGroup& other,
      std::vector<std::pair<const void*, const void*>>& already_compared_obj) const override {
    const Group* pointer = dynamic_cast<const Group*>(&other);
    return pointer != nullptr && urx::detail::Group<Event>::operator==(*pointer) &&
           IGroup::secureComparison(other, already_compared_obj);
  }
};

}  // namespace uac
